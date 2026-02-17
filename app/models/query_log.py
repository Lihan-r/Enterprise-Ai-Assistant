"""
query_log.py - Database Model for Query Logging

This is like a JPA @Entity class in Spring Boot.

Java equivalent:
    @Entity
    @Table(name = "query_logs")
    public class QueryLog {
        @Id @GeneratedValue
        private Long id;
        private String question;
        ...
    }

In Python with SQLAlchemy, we use class attributes instead of
annotations, but the concept is identical.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from app.database import Base


class QueryLog(Base):
    """Stores every question asked to the assistant and its response."""

    # This is like @Table(name = "query_logs")
    __tablename__ = "query_logs"

    # Columns — similar to JPA column annotations
    # In Java: @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # The user's question
    question = Column(Text, nullable=False)

    # The AI-generated answer
    answer = Column(Text, nullable=True)

    # Which documents were used as context (stored as comma-separated IDs for now)
    source_documents = Column(Text, nullable=True)

    # How long the query took (in seconds)
    response_time = Column(Float, nullable=True)

    # Timestamp — like @CreationTimestamp in Spring
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # In Java you'd write toString() — Python uses __repr__
    def __repr__(self):
        return f"<QueryLog(id={self.id}, question='{self.question[:50]}...')>"
