"""Global exception handler middleware"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.exceptions import LLMServiceError, RateLimitError, ValidationError
from app.core.logging import log_security_event


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Global error handler for application exceptions"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle exceptions"""
        try:
            response = await call_next(request)
            return response
        except LLMServiceError as e:
            # LLM service errors → 503
            request_id = getattr(request.state, "request_id", "unknown")
            log_security_event(
                "llm_service_error",
                severity="ERROR",
                message=str(e),
                request_id=request_id,
                path=str(request.url)
            )
            return JSONResponse(
                status_code=503,
                content={
                    "error": "service_unavailable",
                    "message": "LLM service is temporarily unavailable",
                    "request_id": request_id
                }
            )
        except RateLimitError as e:
            # Rate limit errors → 429 (usually handled by middleware directly)
            request_id = getattr(request.state, "request_id", "unknown")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": str(e),
                    "request_id": request_id
                }
            )
        except ValidationError as e:
            # Validation errors → 422
            request_id = getattr(request.state, "request_id", "unknown")
            log_security_event(
                "validation_error",
                severity="WARNING",
                message=str(e),
                request_id=request_id,
                path=str(request.url)
            )
            return JSONResponse(
                status_code=422,
                content={
                    "error": "validation_error",
                    "message": str(e),
                    "request_id": request_id
                }
            )
        except Exception as e:
            # Unexpected errors → 500
            request_id = getattr(request.state, "request_id", "unknown")
            log_security_event(
                "unexpected_error",
                severity="CRITICAL",
                message=str(e),
                request_id=request_id,
                path=str(request.url),
                error_type=type(e).__name__
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "request_id": request_id
                }
            )
