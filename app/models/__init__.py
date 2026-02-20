"""
__init__.py makes this folder a Python "package" (like a Java package).
We import models here so other files can do:
    from app.models import QueryLog
instead of:
    from app.models.query_log import QueryLog
"""

from app.models.query_log import QueryLog
from app.models.document import Document, DocumentChunk

__all__ = ["QueryLog", "Document", "DocumentChunk"]
