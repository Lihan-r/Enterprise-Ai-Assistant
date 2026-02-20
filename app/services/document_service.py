"""
document_service.py - Document Ingestion Pipeline

This service owns the full lifecycle of a document:
    upload → extract text → chunk → embed → store → delete

Java/Spring analogy: this is a @Service class that coordinates between
a repository (the DB session) and other services (embedding, text processing).
It's the equivalent of a Spring @Transactional service method.
"""

import os
from pathlib import Path
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk
from app.services.embedding_service import embedding_service
from app.utils.text_processing import (
    extract_text_from_pdf,
    extract_text_from_txt,
    chunk_text,
)


class DocumentService:
    """Handles document ingestion, retrieval, and deletion."""

    def process_document(self, file_path: str, filename: str, db: Session) -> Document:
        """
        Full ingestion pipeline for a single document.

        Steps:
            1. Detect file type from extension
            2. Extract raw text
            3. Split into overlapping chunks
            4. Generate embeddings for all chunks (batched)
            5. Persist Document + DocumentChunk records to DB

        Args:
            file_path: Path to the saved file on disk
            filename:  Sanitized original filename (used to detect type)
            db:        SQLAlchemy session (injected by FastAPI)

        Returns:
            The newly created Document record
        """
        # Step 1: detect type
        extension = Path(filename).suffix.lower()
        if extension == ".pdf":
            file_type = "pdf"
            text = extract_text_from_pdf(file_path)
        elif extension == ".txt":
            file_type = "txt"
            text = extract_text_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: '{extension}'. Accepted: .pdf, .txt")

        # Step 2 & 3: chunk the text
        chunks = chunk_text(text)
        if not chunks:
            raise ValueError("No text could be extracted from the document.")

        # Step 4: embed all chunks in one batch call (much faster than one-by-one)
        embeddings = embedding_service.generate_embeddings(chunks)

        # Step 5: save to DB inside the caller's transaction
        document = Document(
            filename=filename,
            file_type=file_type,
            chunk_count=len(chunks),
        )
        db.add(document)
        db.flush()  # get document.id without committing

        chunk_records = [
            DocumentChunk(
                document_id=document.id,
                content=chunk_text_content,
                chunk_index=i,
                embedding=embedding,
            )
            for i, (chunk_text_content, embedding) in enumerate(zip(chunks, embeddings))
        ]
        db.add_all(chunk_records)
        db.commit()
        db.refresh(document)

        return document

    def get_all_documents(self, db: Session) -> list[Document]:
        """
        Return all documents (metadata only, no chunks).

        Java analogy: documentRepository.findAll()
        """
        return db.query(Document).order_by(Document.created_at.desc()).all()

    def delete_document(self, document_id: int, db: Session) -> None:
        """
        Delete a document's file from disk and its records from the DB.

        Order matters:
            1. Delete file from disk first.
               If the DB delete then fails, the file is gone but records remain
               — a recoverable inconsistency (re-upload fixes it).
            2. Delete DB records second (cascade removes chunks automatically).
               The reverse order (DB first, then disk) risks orphaned files
               if the disk delete fails after a successful DB commit.

        Args:
            document_id: Primary key of the document to delete
            db:          SQLAlchemy session

        Raises:
            ValueError: If no document with that ID exists
        """
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document with id={document_id} not found.")

        # Step 1: remove the file from disk
        file_path = Path("documents") / document.filename
        if file_path.exists():
            os.remove(file_path)

        # Step 2: delete DB record (chunks cascade automatically via relationship)
        db.delete(document)
        db.commit()


# Singleton instance
document_service = DocumentService()
