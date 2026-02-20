"""
text_processing.py - Text Extraction and Chunking Utilities

These are stateless helper functions (like static utility methods in Java).
They handle two jobs:
1. Extracting raw text from different file types
2. Splitting long text into overlapping chunks for embedding

Why overlapping chunks?
    If a chunk boundary falls mid-sentence, the next chunk starts slightly
    earlier (overlap) so no context is lost at the edges.
    Think of it like a sliding window over the text.
"""

import re
from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file.

    Args:
        file_path: Absolute or relative path to the PDF

    Returns:
        All text content joined from every page
    """
    reader = PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def extract_text_from_txt(file_path: str) -> str:
    """
    Read a plain text file.

    Args:
        file_path: Path to the .txt file

    Returns:
        Full file contents as a string
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks, preferring sentence boundaries.

    Strategy:
        1. Split on sentence-ending punctuation (. ! ?)
        2. Accumulate sentences until we hit chunk_size characters
        3. Start the next chunk `overlap` characters before the end of the last one

    Args:
        text:       The full document text
        chunk_size: Target character count per chunk (default 500)
        overlap:    How many characters to repeat at the start of the next chunk

    Returns:
        List of text chunk strings

    Example (Java analogy):
        Like List<String> chunks = TextUtils.splitIntoChunks(text, 500, 50);
    """
    if not text or not text.strip():
        return []

    # Split into sentences on ., !, or ? followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # If adding this sentence keeps us under chunk_size, append it
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk = (current_chunk + " " + sentence).strip()
        else:
            # Save the current chunk if it has content
            if current_chunk:
                chunks.append(current_chunk)
                # Start next chunk with overlap from the end of the previous chunk
                current_chunk = current_chunk[-overlap:] + " " + sentence
                current_chunk = current_chunk.strip()
            else:
                # Single sentence longer than chunk_size — include it as-is
                chunks.append(sentence)
                current_chunk = sentence[-overlap:]

    # Don't forget the last chunk
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks
