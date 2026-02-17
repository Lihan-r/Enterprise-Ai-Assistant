"""
gemini_service.py - Google Gemini LLM Integration

This service wraps the Gemini API so the rest of the app
doesn't need to know the details of how we talk to the LLM.

In Spring Boot terms, this is like a @Service class.
If you ever want to swap Gemini for OpenAI or Hugging Face,
you only change this one file.
"""

import google.generativeai as genai
from app.config import settings


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

        # Initialize the model
        # gemini-2.0-flash is fast and cheap — good for development
        self.model = genai.GenerativeModel("gemini-2.0-flash")

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
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error communicating with Gemini: {str(e)}"

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
