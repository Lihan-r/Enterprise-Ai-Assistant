"""
document.py - Database Models for Document Storage

Two tables work together here:
- Document      = metadata about an uploaded file (like a JPA @Entity)
- DocumentChunk = the actual text pieces with their vector embeddings

Java/Spring analogy:
    @Entity @Table(name="documents")
    public class Document { ... }

    @Entity @Table(name="document_chunks")
    public class DocumentChunk {
        @ManyToOne
        private Document document;
        ...
    }

The Vector(384) column is provided by pgvector — it stores a 384-dimensional
float array that represents the semantic meaning of a text chunk.
384 matches the output size of the all-MiniLM-L6-v2 embedding model.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.database import Base


class Document(Base):
    """Metadata for an uploaded file."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Original filename (sanitized before saving)
    filename = Column(String(255), nullable=False)

    # "pdf" or "txt"
    file_type = Column(String(50), nullable=False)

    # How many chunks the document was split into
    chunk_count = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # One Document has many DocumentChunks
    # cascade="all, delete-orphan" means deleting a Document also deletes its chunks
    # — like @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true) in JPA
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', chunks={self.chunk_count})>"


class DocumentChunk(Base):
    """A single text chunk from a document, with its vector embedding."""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key back to Document — like @ManyToOne in JPA
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)

    # The actual text content of this chunk
    content = Column(Text, nullable=False)

    # Position of this chunk within the document (0-based)
    chunk_index = Column(Integer, nullable=False)

    # The 384-dimensional vector embedding from sentence-transformers
    # pgvector stores this as a native Postgres vector type for fast similarity search
    embedding = Column(Vector(384), nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Back-reference to the parent Document
    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index})>"
