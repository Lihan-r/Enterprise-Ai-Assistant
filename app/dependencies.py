"""
dependencies.py - Reusable FastAPI Dependencies

In Spring Boot, you'd use a filter or interceptor for API key auth.
In FastAPI, we use a "dependency" — a callable that runs before the
route handler. If it raises an exception, the request is rejected.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings

# Rate limiter — created here so both main.py and route files can import it
# without circular dependencies (like a shared @Bean in Spring)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
)

# auto_error=False so we can return a friendlier message ourselves
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(
    api_key: str | None = Depends(_api_key_header),
) -> None:
    """
    Dependency that enforces API key authentication.

    - If settings.api_key is empty → auth is disabled (dev mode).
    - If the key is missing or wrong → 401 Unauthorized.
    """
    # Dev mode: no key configured, skip auth entirely
    if not settings.api_key:
        return

    if not api_key or api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide a valid X-API-Key header.",
        )
