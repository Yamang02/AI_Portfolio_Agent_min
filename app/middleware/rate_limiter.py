"""Rate limiting middleware using sliding window algorithm"""

import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.exceptions import RateLimitError


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter"""
    
    def __init__(self, rpm: int = 60):
        """
        Initialize rate limiter
        
        Args:
            rpm: Requests per minute allowed per IP
        """
        self.rpm = rpm
        self.window_size = 60  # 1 minute in seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> tuple[bool, int]:
        """
        Check if request from client IP is allowed
        
        Args:
            client_ip: Client IP address
            
        Returns:
            (allowed: bool, retry_after: int seconds)
        """
        now = time.time()
        
        # Clean old requests outside the window
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if now - req_time < self.window_size
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= self.rpm:
            # Calculate retry after (when oldest request leaves window)
            oldest_request = self.requests[client_ip][0]
            retry_after = int(self.window_size - (now - oldest_request)) + 1
            return False, retry_after
        
        # Add current request
        self.requests[client_ip].append(now)
        return True, 0


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting by IP address"""
    
    def __init__(self, app, rpm: int = 60):
        super().__init__(app)
        self.limiter = SlidingWindowRateLimiter(rpm=rpm)
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Get client IP (support X-Forwarded-For for proxies)
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        allowed, retry_after = self.limiter.is_allowed(client_ip)
        
        if not allowed:
            request_id = getattr(request.state, "request_id", "unknown")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded. Max {self.limiter.rpm} requests per minute.",
                    "request_id": request_id
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Process request
        response = await call_next(request)
        return response
