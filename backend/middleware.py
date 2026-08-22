from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
try:
    from backend.config import settings
except ImportError:
    from config import settings
import logging

logger = logging.getLogger(__name__)

class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_upload_size: int = settings.MAX_REQUEST_BODY_SIZE):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.max_upload_size:
                    logger.warning(f"Rejected payload too large: {length} bytes from {request.client.host if request.client else 'unknown'}")
                    return JSONResponse(
                        status_code=413,
                        content={"error": "Payload too large. Maximum allowed size is 10 KB."}
                    )
            except ValueError:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid Content-Length header"}
                )

        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
