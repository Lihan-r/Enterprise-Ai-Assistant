"""
logging.py - Request/Response Logging Middleware

Logs every HTTP request in a compact access-log format:
    POST /query/ 200 142.3ms 127.0.0.1

In Spring Boot, this is similar to a HandlerInterceptor or a Servlet Filter.
In FastAPI/Starlette, we subclass BaseHTTPMiddleware.
"""

import logging
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.access")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip noisy static-file requests for the frontend UI
        if request.url.path.startswith("/ui"):
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            "%s %s %s %.1fms %s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            client_ip,
        )

        return response
