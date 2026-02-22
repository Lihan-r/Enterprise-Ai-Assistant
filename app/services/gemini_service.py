"""
gemini_service.py - Google Gemini LLM Integration

This service wraps the Gemini API so the rest of the app
doesn't need to know the details of how we talk to the LLM.

In Spring Boot terms, this is like a @Service class.
If you ever want to swap Gemini for OpenAI or Hugging Face,
you only change this one file.
"""

import logging

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Handles all communication with Google's Gemini API."""

    def __init__(self):
        """
        Constructor — like a Java constructor.
        In Python, __init__ is the equivalent of:
            public GeminiService() { ... }
        """
        # Configure the API key
        genai.configure(api_key=settings.gemini_api_key)

        # Initialize the model (configurable via GEMINI_MODEL in .env)
        self.model = genai.GenerativeModel(settings.gemini_model)

    def generate_response(self, prompt: str) -> str:
        """
        Send a prompt to Gemini and get a response.

        Args:
            prompt: The text to send to the LLM

        Returns:
            The LLM's response as a string

        '-> str' is a Python type hint — like declaring the return
        type in Java. It's optional but good practice.
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": settings.gemini_temperature,
                    "max_output_tokens": settings.gemini_max_output_tokens,
                },
            )
            if response.usage_metadata:
                logger.info(
                    "Gemini tokens — prompt: %d, response: %d, total: %d",
                    response.usage_metadata.prompt_token_count,
                    response.usage_metadata.candidates_token_count,
                    response.usage_metadata.total_token_count,
                )
            return response.text
        except GoogleAPIError as e:
            raise HTTPException(status_code=502, detail=f"Gemini API error: {e}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid request: {e}")

    def generate_with_context(self, question: str, context: str) -> str:
        """
        This is the key RAG method — we'll use this heavily in Phase 3.

        It takes the user's question PLUS relevant document chunks
        (the 'context') and asks Gemini to answer based on that context.

        This is what makes RAG powerful — the LLM doesn't hallucinate
        because it has real documents to reference.
        """
        prompt = f"""You are an enterprise AI assistant. Answer the question 
based ONLY on the provided context. If the context doesn't contain 
enough information to answer, say "I don't have enough information 
to answer that question."

Context:
{context}

Question: {question}

Answer:"""

        return self.generate_response(prompt)


# Create a single instance (like a Spring @Bean / singleton)
gemini_service = GeminiService()
