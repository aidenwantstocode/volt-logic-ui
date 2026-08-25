import logging
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Request, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
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
    try:
        init_db()
    except Exception as db_err:
        logger.error(f"Database initialization warning: {db_err}")
    # Initialize ML service
    _ = classifier_service
    logger.info(f"VOLT-LOGIC API initialized (Model Version: {settings.MODEL_VERSION})")
    yield
    logger.info("Shutting down VOLT-LOGIC API...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Operational Telemetry & ML Battery Diagnostic API for EV Logistics Fleets",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Attach rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Custom Exception Handlers for hardened security and clear developer feedback
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

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": f"Endpoint '{request.url.path}' was not found.",
                "available_endpoints": {
                    "root": ["/", "/api"],
                    "health": ["/api/health", "/health"],
                    "predict": ["/api/predict", "/predict"],
                    "history": ["/api/history", "/history"],
                    "docs": "/docs",
                    "redoc": "/redoc"
                }
            }
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail if isinstance(exc.detail, str) else "HTTP Exception", "detail": exc.detail}
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

# 3. CORS restriction - Allow all standard web frontend dev/prod origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS", "HEAD"],
    allow_headers=["*"],
)

# ----------------- REUSABLE ROUTE HANDLERS ----------------- #

async def handle_root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "model_version": settings.MODEL_VERSION,
        "docs_url": "/docs",
        "endpoints": {
            "health": ["/api/health", "/health"],
            "predict": ["/api/predict", "/predict"],
            "history": ["/api/history", "/history"],
            "docs": "/docs"
        }
    }

async def handle_health():
    return HealthResponse(ok=True, app=settings.APP_NAME, version="1.0.0")

async def handle_predict(telemetry: TelemetryIn):
    try:
        result = classifier_service.predict(telemetry)
        return result
    except ModelInferenceError:
        raise
    except Exception as e:
        logger.error(f"Unexpected prediction failure: {e}")
        raise ModelInferenceError("ML inference failure")

async def handle_get_history(
    company: Optional[str],
    batteryType: Optional[str],
    battery_type: Optional[str],
    db: Session
):
    target_battery = batteryType or battery_type
    
    query = db.query(Inspection)
    if company and company.strip():
        query = query.filter(Inspection.company == company.strip())
    if target_battery and target_battery.strip():
        query = query.filter(Inspection.battery_type == target_battery.strip())
    
    inspections = query.order_by(Inspection.created_at.desc()).limit(50).all()
    return inspections

async def handle_save_history(record: HistoryCreateRequest, db: Session):
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


# ----------------- ROUTES & ALIASES ----------------- #

# 1. Root Info Endpoints
@app.get("/", summary="API Root Status", tags=["System"])
@app.get("/api", summary="API Root Status (Alias)", tags=["System"], include_in_schema=False)
@app.get("/api/", summary="API Root Status (Alias)", tags=["System"], include_in_schema=False)
async def api_root():
    return await handle_root()


# 2. Health Check Endpoints
@app.get("/api/health", response_model=HealthResponse, summary="Liveness check for uptime monitors & judges", tags=["System"])
@app.get("/health", response_model=HealthResponse, summary="Liveness check (Direct alias)", tags=["System"], include_in_schema=False)
@app.get("/api/health/", response_model=HealthResponse, include_in_schema=False)
@app.get("/health/", response_model=HealthResponse, include_in_schema=False)
async def health():
    return await handle_health()


# 3. ML Battery Telemetry Prediction Endpoints
@app.post("/api/predict", response_model=PredictResponse, summary="Run electrical & thermal battery telemetry through ML model", tags=["ML Inference"])
@app.post("/predict", response_model=PredictResponse, summary="Run prediction (Direct alias)", tags=["ML Inference"], include_in_schema=False)
@app.post("/api/predict/", response_model=PredictResponse, include_in_schema=False)
@app.post("/predict/", response_model=PredictResponse, include_in_schema=False)
@limiter.limit(settings.RATE_LIMIT_PREDICT)
async def predict(request: Request, telemetry: TelemetryIn):
    return await handle_predict(telemetry)


# 4. History Query Endpoints
@app.get("/api/history", response_model=List[HistoryItem], summary="Return past inspection logs (max 50)", tags=["History"])
@app.get("/history", response_model=List[HistoryItem], summary="Return past inspection logs (Direct alias)", tags=["History"], include_in_schema=False)
@app.get("/api/history/", response_model=List[HistoryItem], include_in_schema=False)
@app.get("/history/", response_model=List[HistoryItem], include_in_schema=False)
@limiter.limit(settings.RATE_LIMIT_HISTORY)
async def get_history(
    request: Request,
    company: Optional[str] = Query(None, description="Company name filter"),
    batteryType: Optional[str] = Query(None, description="Battery type filter (camelCase)"),
    battery_type: Optional[str] = Query(None, description="Battery type filter (snake_case)"),
    db: Session = Depends(get_db)
):
    return await handle_get_history(company, batteryType, battery_type, db)


# 5. History Save Endpoints
@app.post("/api/history", response_model=HistoryItem, status_code=status.HTTP_201_CREATED, summary="Save a new inspection record into database", tags=["History"])
@app.post("/history", response_model=HistoryItem, status_code=status.HTTP_201_CREATED, summary="Save inspection record (Direct alias)", tags=["History"], include_in_schema=False)
@app.post("/api/history/", response_model=HistoryItem, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@app.post("/history/", response_model=HistoryItem, status_code=status.HTTP_201_CREATED, include_in_schema=False)
@limiter.limit(settings.RATE_LIMIT_HISTORY)
async def save_history(
    request: Request,
    record: HistoryCreateRequest,
    db: Session = Depends(get_db)
):
    return await handle_save_history(record, db)
