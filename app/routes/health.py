"""
health.py - Health Check Routes

In Spring Boot, you might use Spring Actuator for /health endpoints.
In FastAPI, we create them manually using a "router" — which is like
a @RestController in Spring.

FastAPI concept mapping:
- APIRouter        = @RestController
- @router.get()    = @GetMapping
- @router.post()   = @PostMapping
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings

# Create a router (like @RestController)
# prefix="/health" means all routes here start with /health
# tags=["Health"] groups them in the auto-generated docs
router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
def health_check():
    """
    Basic health check — just confirms the server is running.

    In Spring: @GetMapping("/health")
    In FastAPI: @router.get("/")

    The function return value is automatically converted to JSON.
    No need for ResponseEntity — FastAPI handles it.
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version
    }


@router.get("/db")
def db_health_check(db: Session = Depends(get_db)):
    """
    Checks if the database connection works.

    Notice 'db: Session = Depends(get_db)' — this is FastAPI's
    dependency injection. It's like @Autowired in Spring.

    FastAPI sees Depends(get_db) and automatically:
    1. Calls get_db() to create a session
    2. Passes it as the 'db' parameter
    3. Closes it when the request is done
    """
    try:
        # Try a simple query
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
