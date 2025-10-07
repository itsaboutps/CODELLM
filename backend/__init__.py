"""
Backend module for Document Assistant RAG

This module contains all the core components for the RAG system:
- RAG Engine: Core retrieval and generation system
- Document Processor: Extract text from various document formats
- Text Chunker: Advanced text splitting with semantic awareness
- Scope Validator: Validate query relevance to uploaded documents
"""

from .rag_engine import RAGEngine
from .document_processor import DocumentProcessor
from .text_chunker import AdvancedTextChunker, TextChunk, ChunkType
from .scope_validator import ScopeValidator

__version__ = "1.0.0"
__author__ = "Document Assistant RAG Team"

__all__ = [
    "RAGEngine",
    "DocumentProcessor", 
    "AdvancedTextChunker",
    "TextChunk",
    "ChunkType",
    "ScopeValidator"
]