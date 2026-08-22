import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Request, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

try:
    from backend.config import settings
    from backend.database import get_db, init_db
    from backend.models import Inspection
    from backend.schemas import (
        TelemetryIn,
        PredictResponse,
        HistoryCreateRequest,
        HistoryItem,
        HealthResponse,
    )
    from backend.ml_model import classifier_service, ModelInferenceError
    from backend.middleware import LimitUploadSizeMiddleware, SecurityHeadersMiddleware
except ImportError:
    from config import settings
    from database import get_db, init_db
    from models import Inspection
    from schemas import (
        TelemetryIn,
        PredictResponse,
        HistoryCreateRequest,
        HistoryItem,
        HealthResponse,
    )
    from ml_model import classifier_service, ModelInferenceError
    from middleware import LimitUploadSizeMiddleware, SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("volt-logic-api")

# Rate Limiter setup
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database schema & tables
    logger.info("Initializing VOLT-LOGIC API and Database tables...")
    init_db()
    # Initialize ML service
    _ = classifier_service
    logger.info(f"VOLT-LOGIC API initialized (Model Version: {settings.MODEL_VERSION})")
    yield
    logger.info("Shutting down VOLT-LOGIC API...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Operational Telemetry & ML Battery Diagnostic API for EV Logistics Fleets",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

# Attach rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom Exception Handlers for hardened security (No stack trace exposure)
@app.exception_handler(ModelInferenceError)
async def model_inference_exception_handler(request: Request, exc: ModelInferenceError):
    logger.error(f"Inference error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": "ML inference service is temporarily unavailable. Please try again."}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    clean_errors = [{"field": ".".join(str(loc) for loc in err.get("loc", [])), "message": err.get("msg")} for err in errors]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Invalid input data", "details": clean_errors}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "An internal server error occurred."}
    )

# Middlewares
# 1. Body upload size limit (10 KB)
app.add_middleware(LimitUploadSizeMiddleware, max_upload_size=settings.MAX_REQUEST_BODY_SIZE)

# 2. Security Headers (nosniff, DENY, etc.)
app.add_middleware(SecurityHeadersMiddleware)

# 3. CORS restriction
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

# ----------------- ROUTES ----------------- #

@app.get(
    "/api/health",
    response_model=HealthResponse,
    summary="Liveness check for uptime monitors & judges",
    tags=["System"]
)
async def health():
    """Returns 200 OK to confirm service liveness."""
    return HealthResponse(ok=True, app=settings.APP_NAME, version="1.0.0")


@app.post(
    "/api/predict",
    response_model=PredictResponse,
    summary="Run electrical & thermal battery telemetry through the ML model",
    tags=["ML Inference"]
)
@limiter.limit(settings.RATE_LIMIT_PREDICT)
async def predict(request: Request, telemetry: TelemetryIn):
    """
    Evaluates battery pack health status (HEALTHY, WARNING, CRITICAL)
    based on voltage, current, temperature, and internal resistance.
    """
    try:
        result = classifier_service.predict(telemetry)
        return result
    except ModelInferenceError:
        raise
    except Exception as e:
        logger.error(f"Unexpected prediction failure: {e}")
        raise ModelInferenceError("ML inference failure")


@app.get(
    "/api/history",
    response_model=List[HistoryItem],
    summary="Return past inspections strictly scoped to company and batteryType (max 50)",
    tags=["History"]
)
@limiter.limit(settings.RATE_LIMIT_HISTORY)
async def get_history(
    request: Request,
    company: Optional[str] = Query(None, description="Company name filter (Required)"),
    batteryType: Optional[str] = Query(None, description="Battery type filter (camelCase)"),
    battery_type: Optional[str] = Query(None, description="Battery type filter (snake_case)"),
    db: Session = Depends(get_db)
):
    """
    Returns past inspection logs for a specified company and battery type.
    Enforces scoped access: requests missing company or batteryType are rejected with 400.
    """
    target_battery = batteryType or battery_type
    # Security Rule 2.1: Never allow unscoped database queries
    if not company or not company.strip() or not target_battery or not target_battery.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both 'company' and 'batteryType' parameters are strictly required to view history."
        )

    clean_company = company.strip()
    clean_battery_type = target_battery.strip()

    # Parameterized ORM query with limit 50
    inspections = (
        db.query(Inspection)
        .filter(
            Inspection.company == clean_company,
            Inspection.battery_type == clean_battery_type
        )
        .order_by(Inspection.created_at.desc())
        .limit(50)
        .all()
    )

    return inspections


@app.post(
    "/api/history",
    response_model=HistoryItem,
    status_code=status.HTTP_201_CREATED,
    summary="Save a new inspection record into database",
    tags=["History"]
)
@limiter.limit(settings.RATE_LIMIT_HISTORY)
async def save_history(
    request: Request,
    record: HistoryCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Saves a completed telemetry inspection record into the PostgreSQL database.
    """
    try:
        new_inspection = Inspection(
            vehicle_id=record.vehicle_id.strip(),
            company=record.company.strip(),
            battery_type=record.battery_type.strip(),
            capacity=record.capacity,
            re=record.re,
            rct=record.rct,
            ambient_temperature=record.ambient_temperature,
            voltage=record.voltage if record.voltage is not None else 0.0,
            current=record.current if record.current is not None else 0.0,
            temperature=record.temperature if record.temperature is not None else record.ambient_temperature,
            resistance=record.resistance if record.resistance is not None else record.re,
            status=record.status,
            confidence=record.confidence,
            model_version=record.model_version or settings.MODEL_VERSION
        )
        db.add(new_inspection)
        db.commit()
        db.refresh(new_inspection)
        return new_inspection
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to persist inspection record: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save inspection record."
        )
