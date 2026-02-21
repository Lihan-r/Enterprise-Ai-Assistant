"""
retrieval_service.py - pgvector Cosine Similarity Search

Finds the top-k document chunks most semantically similar to a query embedding.

The SQL uses an explicit CAST(:query_vec AS vector) rather than relying on
Postgres to silently coerce a string — silent coercion can produce confusing
errors and is not guaranteed across pgvector versions.

The cosine distance operator (<=> in pgvector) returns values in [0, 2]:
  0   = identical vectors
  2   = opposite vectors
similarity_score = 1 - distance maps this to [−1, 1], with 1 being most similar.
"""

import json
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


class RetrievalService:
    def find_similar_chunks(
        self,
        query_embedding: list[float],
        db: Session,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Return the top_k document chunks closest to query_embedding.

        Args:
            query_embedding: 384-dimensional float list from embedding_service.
            db:              SQLAlchemy session (injected by FastAPI dependency).
            top_k:           Number of results to return (caller must validate bounds).

        Returns:
            List of dicts with keys: content, document_id, chunk_index, similarity_score.
        """
        # Serialize to JSON array string so Postgres can parse it as a vector literal.
        # The explicit CAST avoids relying on implicit type coercion.
        embedding_str = json.dumps(query_embedding)

        sql = text(
            """
            SELECT id, document_id, content, chunk_index,
                   embedding <=> CAST(:query_vec AS vector) AS distance
            FROM document_chunks
            ORDER BY embedding <=> CAST(:query_vec AS vector)
            LIMIT :limit
            """
        )

        try:
            rows = db.execute(sql, {"query_vec": embedding_str, "limit": top_k}).fetchall()
        except Exception as exc:
            logger.error("pgvector similarity search failed: %s", exc)
            raise

        return [
            {
                "content": row.content,
                "document_id": row.document_id,
                "chunk_index": row.chunk_index,
                # Convert cosine distance → similarity score
                "similarity_score": round(1.0 - float(row.distance), 4),
            }
            for row in rows
        ]


retrieval_service = RetrievalService()
