from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.routers import chat

# Configure logging
settings = get_settings()
configure_logging(level=settings.log_level)

# Create FastAPI app
app = FastAPI(
    title="Local LLM Server",
    description="AI agent server with LLM integration",
    version="1.0.0"
)

# CORS configuration
origins = settings.allowed_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - process from bottom to top)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimiterMiddleware, rpm=settings.rate_limit_rpm)
app.add_middleware(RequestIDMiddleware)

# Include routers
app.include_router(chat.router, prefix="/api")


@app.get("/health", tags=["health"])
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "local-llm-server"}
