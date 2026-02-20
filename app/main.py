"""
main.py - Application Entry Point

This is the equivalent of your Spring Boot main class:

    @SpringBootApplication
    public class Application {
        public static void main(String[] args) {
            SpringApplication.run(Application.class, args);
        }
    }

In FastAPI, we create an app instance and register routes (routers).
FastAPI also auto-generates API docs at /docs — like Swagger/OpenAPI
in Spring Boot, but with zero configuration.
"""

import logging
from fastapi import FastAPI
from app.config import settings
from app.database import engine, Base
from app.routes.health import router as health_router

logger = logging.getLogger(__name__)

# Create the FastAPI app (like SpringApplication)
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered assistant that answers internal company questions using RAG.",
)

# Create database tables on startup
# In Spring Boot, JPA does this with spring.jpa.hibernate.ddl-auto=update
# Here we do it explicitly — wrapped so a DB outage doesn't crash the server
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.warning("Could not create DB tables at startup: %s", e)

# Register routers (like @ComponentScan finding your @RestControllers)
app.include_router(health_router)


# Root endpoint — a simple welcome message
@app.get("/")
def root():
    """
    You can define routes directly on the app too,
    not just on routers. This is the simplest form.
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "Visit /docs for interactive API documentation"
    }
