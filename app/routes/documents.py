"""
documents.py - Document Upload / List / Delete Routes

FastAPI concept mapping:
- APIRouter         = @RestController
- UploadFile        = MultipartFile in Spring MVC
- Depends(get_db)   = @Autowired repository / EntityManager

Security note:
    We sanitize the uploaded filename with Path(file.filename).name before
    saving. This strips any directory components (e.g. "../../app/main.py"
    becomes "main.py"), preventing path traversal attacks.
"""

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.document_service import document_service

router = APIRouter(prefix="/documents", tags=["Documents"])

# Where uploaded files are stored on disk
DOCUMENTS_DIR = Path("documents")


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a document (.pdf or .txt), process it, and store embeddings.

    The full pipeline runs synchronously:
        save file → extract text → chunk → embed → store in DB

    Returns document metadata and the number of chunks created.
    """
    # Sanitize filename — strips directory components to prevent path traversal
    safe_name = Path(file.filename).name
    if not safe_name:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    extension = Path(safe_name).suffix.lower()
    if extension not in {".pdf", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Upload a .pdf or .txt file.",
        )

    # Save the uploaded file to disk
    save_path = DOCUMENTS_DIR / safe_name
    content = await file.read()
    save_path.write_bytes(content)

    # Run the ingestion pipeline
    try:
        document = document_service.process_document(
            file_path=str(save_path),
            filename=safe_name,
            db=db,
        )
    except ValueError as e:
        # Clean up the file if processing failed
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        if save_path.exists():
            save_path.unlink()
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    return {
        "message": "Document uploaded and processed successfully.",
        "document": {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "chunk_count": document.chunk_count,
            "created_at": document.created_at.isoformat(),
        },
    }


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    """
    List all uploaded documents (metadata only).

    Java analogy: GET /documents → documentRepository.findAll()
    """
    documents = document_service.get_all_documents(db)
    return {
        "count": len(documents),
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "chunk_count": doc.chunk_count,
                "created_at": doc.created_at.isoformat(),
            }
            for doc in documents
        ],
    }


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)):
    """
    Delete a document and all its chunks from the DB, and remove the file from disk.

    Java analogy: DELETE /documents/{id} → documentRepository.deleteById(id)
    """
    try:
        document_service.delete_document(document_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"message": f"Document {document_id} deleted successfully."}
