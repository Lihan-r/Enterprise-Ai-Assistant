"""
database.py - PostgreSQL Database Connection

In Spring Boot, you configure a DataSource and JPA handles the rest.
In Python, we use SQLAlchemy — it's the equivalent of Hibernate/JPA.

Key concepts (Java equivalents):
- engine         = DataSource (the connection pool)
- SessionLocal   = EntityManager (handles DB operations)
- Base           = @Entity base class
- get_db()       = Dependency injection of EntityManager
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings


# Create the database engine (connection pool)
# In Spring this happens automatically — here we do it explicitly
engine = create_engine(
    settings.database_url,
    echo=settings.debug  # Prints SQL queries when debug=True (like spring.jpa.show-sql=true)
)

# Session factory — creates new database sessions
# autocommit=False means you control when changes are saved (like @Transactional)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for all database models
# In Java: every @Entity extends a base — same idea here
class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependency that provides a database session to each request.

    In Spring, you'd use @Autowired to inject a repository.
    In FastAPI, this function is injected into route handlers.

    The 'yield' keyword is Python-specific:
    - It gives the session to the route
    - After the route finishes, it closes the session
    - Think of it like try-with-resources in Java
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
