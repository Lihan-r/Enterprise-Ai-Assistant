"""
embedding_service.py - Text Embedding via Sentence Transformers

This service converts text into numerical vectors (embeddings).
Two texts with similar meaning will have vectors that are close together
in 384-dimensional space — that's what makes semantic search possible.

Java/Spring analogy: this is a @Service that wraps an ML model instead of
an HTTP client or repository.

Model: all-MiniLM-L6-v2
    - Fast and lightweight (good for development)
    - Outputs 384-dimensional vectors
    - Downloads automatically on first use (~90 MB, cached after that)
"""

from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """Wraps the sentence-transformers model for generating text embeddings."""

    def __init__(self):
        """
        Load the model on startup.
        The model is cached locally after the first download so subsequent
        startups are instant.
        """
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def generate_embedding(self, text: str) -> list[float]:
        """
        Convert a single text string into a 384-dimensional vector.

        Args:
            text: Any text string (sentence, paragraph, etc.)

        Returns:
            List of 384 floats representing the semantic content of the text
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Convert a list of texts into embeddings in one efficient batch call.

        Batch processing is significantly faster than calling generate_embedding
        in a loop — the model processes all texts in parallel on the GPU/CPU.

        Args:
            texts: List of text strings to embed

        Returns:
            List of 384-float vectors, one per input text
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True, batch_size=32)
        return [e.tolist() for e in embeddings]


# Singleton — loaded once at startup, reused for every request
# Like a @Bean(scope = "singleton") in Spring
embedding_service = EmbeddingService()
