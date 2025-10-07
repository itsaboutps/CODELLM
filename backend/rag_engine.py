"""
RAG Engine - Core Retrieval Augmented Generation System

Integrates document processing, vector storage, retrieval, and LLM generation
with advanced scope validation for accurate document-based Q&A.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np

# Import with error handling
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Using fallback embedding.")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb not available. Using in-memory storage.")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import torch
    from transformers import AutoTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available. Using fallback LLM.")

from .document_processor import DocumentProcessor
from .scope_validator import ScopeValidator
from .text_chunker import AdvancedTextChunker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Advanced RAG Engine with state-of-the-art components:
    - Sentence Transformers for embeddings (all-MiniLM-L6-v2)
    - ChromaDB for vector storage
    - Multiple LLM options (OpenAI GPT, Hugging Face models)
    - Advanced text chunking and scope validation
    """
    
    def __init__(self, 
                 embedding_model_name: str = "all-MiniLM-L6-v2",
                 llm_provider: str = "huggingface",
                 llm_model: str = "microsoft/DialoGPT-medium"):
        """
        Initialize the RAG Engine with best-practice configurations.
        
        Args:
            embedding_model_name: Name of the sentence transformer model
            llm_provider: "openai" or "huggingface"
            llm_model: Model name for the LLM
        """
        
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.text_chunker = AdvancedTextChunker()
        self.scope_validator = ScopeValidator()
        
        # Initialize embedding model (free and high-quality)
        logger.info(f"Loading embedding model: {embedding_model_name}")
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(embedding_model_name)
            except Exception as e:
                logger.error(f"Error loading sentence transformer: {e}")
                self.embedding_model = None
        else:
            logger.warning("Using simple keyword-based similarity instead of embeddings")
            self.embedding_model = None
        
        # Initialize vector database
        if CHROMADB_AVAILABLE:
            try:
                self.chroma_client = chromadb.PersistentClient(
                    path="./chroma_db",
                    settings=Settings(anonymized_telemetry=False)
                )
                
                # Create or get collection
                self.collection = self.chroma_client.get_or_create_collection(
                    name="document_embeddings",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("ChromaDB initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing ChromaDB: {e}")
                # Fallback to in-memory storage
                self.collection = None
                self.document_chunks = []  # Simple list for fallback
        else:
            logger.warning("Using simple in-memory storage instead of ChromaDB")
            self.collection = None
            self.document_chunks = []  # Simple list for fallback
        
        # Always initialize document_chunks for fallback scenarios
        if not hasattr(self, 'document_chunks'):
            self.document_chunks = []
        
        # Initialize LLM
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self._initialize_llm()
        
        logger.info("RAG Engine initialized successfully")
    
    def _initialize_llm(self):
        """Initialize the Language Model based on provider choice."""
        if self.llm_provider == "openai":
            # OpenAI GPT (requires API key)
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.llm_client = OpenAI(api_key=api_key)
                logger.info("OpenAI LLM initialized")
            else:
                logger.warning("OpenAI API key not found, falling back to Hugging Face")
                self.llm_provider = "huggingface"
        
        if self.llm_provider == "huggingface":
            # Free Hugging Face models
            if TRANSFORMERS_AVAILABLE:
                try:
                    # Use a lighter, faster model for better performance
                    model_name = "microsoft/DialoGPT-small"  # Smaller, faster model
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    
                    # Add pad token if it doesn't exist
                    if self.tokenizer.pad_token is None:
                        self.tokenizer.pad_token = self.tokenizer.eos_token
                    
                    # Use pipeline for easier text generation
                    self.llm_pipeline = pipeline(
                        "text-generation",
                        model=model_name,
                        tokenizer=self.tokenizer,
                        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                        device_map="auto" if torch.cuda.is_available() else None,
                        max_new_tokens=256,
                        do_sample=True,
                        temperature=0.7,
                        pad_token_id=self.tokenizer.eos_token_id
                    )
                    logger.info(f"Hugging Face LLM initialized: {model_name}")
                except Exception as e:
                    logger.error(f"Error initializing Hugging Face model: {e}")
                    # Fallback to a simpler approach
                    self.llm_pipeline = None
            else:
                logger.warning("Transformers not available, using template-based responses")
                self.llm_pipeline = None
    
    def add_document(self, uploaded_file) -> bool:
        """
        Process and add a document to the RAG system.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            bool: Success status
        """
        try:
            # Extract text from document
            text_content = self.document_processor.extract_text(uploaded_file)
            if not text_content:
                logger.error(f"No text extracted from {uploaded_file.name}")
                return False
            
            # Chunk the text using advanced chunking
            chunks = self.text_chunker.chunk_text(text_content)
            logger.info(f"Created {len(chunks)} chunks from {uploaded_file.name}")
            
            # Store chunks
            chunk_texts = [chunk.content for chunk in chunks]
            
            if self.collection is not None and self.embedding_model is not None:
                # Use vector database with embeddings
                embeddings = self.embedding_model.encode(chunk_texts, convert_to_tensor=False)
                
                # Prepare metadata
                metadatas = []
                ids = []
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{uploaded_file.name}_{i}"
                    metadata = {
                        "document": uploaded_file.name,
                        "chunk_index": i,
                        "start_char": chunk.start_index,
                        "end_char": chunk.end_index,
                        "content_type": chunk.content_type
                    }
                    metadatas.append(metadata)
                    ids.append(chunk_id)
                
                # Add to vector database
                self.collection.add(
                    embeddings=embeddings.tolist(),
                    metadatas=metadatas,
                    documents=chunk_texts,
                    ids=ids
                )
            else:
                # Use simple in-memory storage as fallback
                for i, chunk in enumerate(chunks):
                    self.document_chunks.append({
                        "content": chunk.content,
                        "document": uploaded_file.name,
                        "chunk_index": i,
                        "start_char": chunk.start_index,
                        "end_char": chunk.end_index,
                        "content_type": chunk.content_type
                    })
            
            logger.info(f"Successfully added {len(chunks)} chunks to vector database")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document {uploaded_file.name}: {e}")
            return False
    
    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """
        Query the RAG system with a question.
        
        Args:
            question: User's question
            k: Number of top chunks to retrieve
            
        Returns:
            Dict containing answer, sources, and scope validation
        """
        try:
            # Check if we have any documents
            has_documents = False
            if self.collection is not None and self.embedding_model is not None:
                try:
                    has_documents = self.collection.count() > 0
                except:
                    has_documents = False
            
            # If no vector DB documents, check fallback storage
            if not has_documents:
                has_documents = len(self.document_chunks) > 0
            
            if not has_documents:
                return {
                    "answer": "I don't have any documents to search. Please upload some documents first.",
                    "sources": [],
                    "in_scope": False
                }
            
            # Check if question is in scope
            if self.collection is not None and self.embedding_model is not None and self.collection.count() > 0:
                scope_result = self.scope_validator.validate_scope(question, self.collection)
            else:
                scope_result = self.scope_validator.validate_scope(question, self.document_chunks)
            
            # Retrieve relevant chunks
            if self.collection is not None and self.embedding_model is not None and self.collection.count() > 0:
                # Use vector database
                question_embedding = self.embedding_model.encode([question], convert_to_tensor=False)
                results = self.collection.query(
                    query_embeddings=question_embedding.tolist(),
                    n_results=min(k, self.collection.count())
                )
                
                if not results['documents'][0]:
                    return {
                        "answer": "I don't have enough information in the uploaded documents to answer your question.",
                        "sources": [],
                        "in_scope": False
                    }
                
                context_chunks = results['documents'][0]
                metadatas = results['metadatas'][0]
            else:
                # Use simple keyword matching as fallback
                context_chunks, metadatas = self._simple_search(question, k)
                
                if not context_chunks:
                    return {
                        "answer": "I don't have enough information in the uploaded documents to answer your question.",
                        "sources": [],
                        "in_scope": False
                    }
            
            context = "\n\n".join([
                f"Document: {meta['document']}\nContent: {chunk}"
                for chunk, meta in zip(context_chunks, metadatas)
            ])
            
            # Generate answer using LLM
            answer = self._generate_answer(question, context, scope_result['in_scope'])
            
            # Prepare sources
            sources = []
            for chunk, meta in zip(context_chunks, metadatas):
                sources.append({
                    "document": meta['document'],
                    "content": chunk[:200] + "..." if len(chunk) > 200 else chunk,
                    "chunk_index": meta['chunk_index']
                })
            
            return {
                "answer": answer,
                "sources": sources,
                "in_scope": scope_result['in_scope']
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "in_scope": True
            }
    
    def _generate_answer(self, question: str, context: str, in_scope: bool) -> str:
        """Generate an answer using the configured LLM."""
        
        if not in_scope:
            return ("I notice your question appears to be outside the scope of the uploaded documents. "
                   "I can only answer questions based on the content of the documents you've provided. "
                   "Please ask questions related to the uploaded documents.")
        
        # Prepare prompt
        prompt = f"""Based on the following context from uploaded documents, please answer the question.
If the answer is not available in the context, please say so.

Context:
{context[:2000]}  # Limit context to avoid token limits

Question: {question}

Answer:"""
        
        try:
            if self.llm_provider == "openai" and hasattr(self, 'llm_client'):
                response = self.llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided document context."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=256,
                    temperature=0.7
                )
                return response.choices[0].message.content
                
            elif self.llm_provider == "huggingface" and self.llm_pipeline:
                # Use Hugging Face pipeline
                response = self.llm_pipeline(
                    prompt,
                    max_new_tokens=256,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.eos_token_id
                )
                generated_text = response[0]['generated_text']
                # Extract only the answer part
                answer = generated_text.replace(prompt, "").strip()
                return answer if answer else "I couldn't generate a proper answer based on the provided context."
            
            else:
                # Fallback: Simple template-based response
                return self._template_based_answer(question, context)
                
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return self._template_based_answer(question, context)
    
    def _template_based_answer(self, question: str, context: str) -> str:
        """Fallback method for generating answers using templates."""
        # Simple keyword-based matching for basic Q&A
        question_lower = question.lower()
        context_lower = context.lower()
        
        if any(word in question_lower for word in ['what', 'define', 'definition']):
            # Look for definitions or explanations
            sentences = context.split('. ')
            relevant_sentences = [s for s in sentences if any(word in s.lower() for word in question_lower.split())]
            if relevant_sentences:
                return '. '.join(relevant_sentences[:2]) + '.'
        
        elif any(word in question_lower for word in ['how', 'process', 'steps']):
            # Look for process descriptions
            sentences = context.split('. ')
            relevant_sentences = [s for s in sentences if any(word in s.lower() for word in ['step', 'process', 'method', 'how'])]
            if relevant_sentences:
                return '. '.join(relevant_sentences[:3]) + '.'
        
        # Default response with context excerpt
        context_excerpt = context[:300] + "..." if len(context) > 300 else context
        return f"Based on the uploaded documents: {context_excerpt}"
    
    def _simple_search(self, question: str, k: int = 5):
        """Simple keyword-based search as fallback when embeddings unavailable."""
        question_words = set(question.lower().split())
        scored_chunks = []
        
        for chunk in self.document_chunks:
            chunk_words = set(chunk["content"].lower().split())
            # Simple jaccard similarity
            intersection = len(question_words.intersection(chunk_words))
            union = len(question_words.union(chunk_words))
            score = intersection / union if union > 0 else 0
            
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Sort by score and take top k
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_chunks = scored_chunks[:k]
        
        context_chunks = [chunk["content"] for chunk, _ in top_chunks]
        metadatas = [{
            "document": chunk["document"],
            "chunk_index": chunk["chunk_index"]
        } for chunk, _ in top_chunks]
        
        return context_chunks, metadatas

    def clear_documents(self):
        """Clear all documents from the storage."""
        try:
            if self.collection is not None:
                # Delete the collection and recreate it
                self.chroma_client.delete_collection("document_embeddings")
                self.collection = self.chroma_client.get_or_create_collection(
                    name="document_embeddings",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("All documents cleared from vector database")
            else:
                # Clear in-memory storage
                self.document_chunks = []
                logger.info("All documents cleared from memory")
        except Exception as e:
            logger.error(f"Error clearing documents: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the current RAG system."""
        try:
            if self.collection is not None:
                count = self.collection.count()
                embedding_dim = self.embedding_model.get_sentence_embedding_dimension() if self.embedding_model else "N/A"
            else:
                count = len(self.document_chunks)
                embedding_dim = "Simple keyword matching"
            
            return {
                "total_chunks": count,
                "embedding_model": embedding_dim,
                "llm_provider": self.llm_provider,
                "llm_model": self.llm_model,
                "vector_db_available": self.collection is not None,
                "embedding_available": self.embedding_model is not None
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}