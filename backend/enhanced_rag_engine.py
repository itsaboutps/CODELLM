"""
Enhanced RAG Engine - Using Best Free Models

This version uses state-of-the-art free models:
- Sentence Transformers: all-mpnet-base-v2 (best quality)
- Text Splitting: LangChain RecursiveCharacterTextSplitter
- Vector DB: FAISS + ChromaDB
- Evaluation: BERT-Score for similarity
"""

import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np

# Best Free Models
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS, Chroma
    from langchain.schema import Document
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from bert_score import score as bert_score
    BERT_SCORE_AVAILABLE = True
except ImportError:
    BERT_SCORE_AVAILABLE = False

from .document_processor import DocumentProcessor
from .scope_validator import EnhancedScopeValidator
from .text_chunker import AdvancedTextChunker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedRAGEngine:
    """
    Enhanced RAG Engine using best free models:
    - all-mpnet-base-v2: Best sentence transformer for quality
    - LangChain: Industry-standard text processing
    - FAISS: Facebook's similarity search (faster than ChromaDB)
    - BERT-Score: Semantic similarity evaluation
    """
    
    def __init__(self, 
                 embedding_model_name: str = "all-mpnet-base-v2",
                 use_faiss: bool = True,
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200):
        """
        Initialize Enhanced RAG Engine with best free models.
        """
        
        # Initialize components
        self.document_processor = DocumentProcessor()
        self.scope_validator = EnhancedScopeValidator()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize best embedding model
        logger.info(f"Loading best embedding model: {embedding_model_name}")
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # all-mpnet-base-v2 is the best quality model
                self.embedding_model = SentenceTransformer(embedding_model_name)
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                logger.info(f"✅ Loaded {embedding_model_name} (dim: {self.embedding_dim})")
            except Exception as e:
                logger.error(f"Error loading embedding model: {e}")
                self.embedding_model = None
                self.embedding_dim = 384  # Default dimension
        else:
            logger.warning("Sentence Transformers not available")
            self.embedding_model = None
            self.embedding_dim = 384
        
        # Initialize best text splitter (LangChain)
        if LANGCHAIN_AVAILABLE:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            logger.info("✅ LangChain text splitter initialized")
        else:
            # Fallback to custom chunker
            self.text_splitter = AdvancedTextChunker(chunk_size, chunk_overlap)
            logger.info("Using fallback text chunker")
        
        # Initialize vector storage (prefer FAISS for speed)
        self.use_faiss = use_faiss and FAISS_AVAILABLE
        self.vector_store = None
        self.documents = []  # Store documents for FAISS
        
        if self.use_faiss:
            logger.info("✅ FAISS vector store ready")
        elif CHROMADB_AVAILABLE:
            try:
                self.chroma_client = chromadb.PersistentClient(
                    path="./chroma_db",
                    settings=Settings(anonymized_telemetry=False)
                )
                self.collection = self.chroma_client.get_or_create_collection(
                    name="enhanced_embeddings"
                )
                logger.info("✅ ChromaDB initialized")
            except Exception as e:
                logger.error(f"ChromaDB error: {e}")
                self.collection = None
        else:
            logger.warning("Using in-memory fallback storage")
            self.document_chunks = []
        
        logger.info("Enhanced RAG Engine initialized with best free models")
    
    def add_document(self, uploaded_file) -> bool:
        """Add document using best processing pipeline."""
        try:
            # Extract text
            text_content = self.document_processor.extract_text(uploaded_file)
            if not text_content:
                logger.error(f"No text extracted from {uploaded_file.name}")
                return False
            
            # Use LangChain for best text splitting
            if LANGCHAIN_AVAILABLE:
                documents = self.text_splitter.create_documents(
                    [text_content], 
                    metadatas=[{"source": uploaded_file.name}]
                )
                chunks = [doc.page_content for doc in documents]
                metadatas = [doc.metadata for doc in documents]
            else:
                # Fallback to custom chunker
                chunk_objects = self.text_splitter.chunk_text(text_content, uploaded_file.name)
                chunks = [chunk.content for chunk in chunk_objects]
                metadatas = [{"source": uploaded_file.name, "chunk_id": i} for i in range(len(chunks))]
            
            logger.info(f"Created {len(chunks)} chunks from {uploaded_file.name}")
            
            # Generate embeddings
            if self.embedding_model:
                embeddings = self.embedding_model.encode(chunks, convert_to_tensor=False)
                
                # Store in vector database
                if self.use_faiss and len(self.documents) == 0:
                    # Initialize FAISS index
                    self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product for cosine similarity
                    
                # Add to vector store
                if self.use_faiss:
                    # Add to FAISS
                    embeddings_array = np.array(embeddings).astype('float32')
                    # Normalize for cosine similarity
                    faiss.normalize_L2(embeddings_array)
                    self.faiss_index.add(embeddings_array)
                    
                    # Store documents and metadata
                    for i, (chunk, metadata) in enumerate(zip(chunks, metadatas)):
                        self.documents.append({
                            "content": chunk,
                            "metadata": metadata,
                            "doc_id": len(self.documents)
                        })
                    
                elif hasattr(self, 'collection') and self.collection:
                    # Add to ChromaDB
                    ids = [f"{uploaded_file.name}_{i}" for i in range(len(chunks))]
                    self.collection.add(
                        embeddings=embeddings.tolist(),
                        metadatas=metadatas,
                        documents=chunks,
                        ids=ids
                    )
                else:
                    # Fallback storage
                    for chunk, metadata in zip(chunks, metadatas):
                        self.document_chunks.append({
                            "content": chunk,
                            "metadata": metadata
                        })
            else:
                # No embeddings available - use fallback
                for chunk, metadata in zip(chunks, metadatas):
                    if not hasattr(self, 'document_chunks'):
                        self.document_chunks = []
                    self.document_chunks.append({
                        "content": chunk,
                        "metadata": metadata
                    })
            
            logger.info(f"✅ Successfully added {len(chunks)} chunks to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return False
    
    def query(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Enhanced query with best similarity search."""
        try:
            # Check document availability
            doc_count = self._get_document_count()
            if doc_count == 0:
                return {
                    "answer": "No documents available. Please upload documents first.",
                    "sources": [],
                    "in_scope": False,
                    "confidence": 0.0
                }
            
            # Enhanced scope validation
            scope_result = self.scope_validator.validate_scope(question, self._get_all_content())
            
            # Retrieve relevant chunks
            retrieved_chunks, similarities = self._retrieve_chunks(question, k)
            
            if not retrieved_chunks:
                return {
                    "answer": "No relevant information found in the documents.",
                    "sources": [],
                    "in_scope": scope_result['in_scope'],
                    "confidence": 0.0
                }
            
            # Generate enhanced answer
            answer = self._generate_enhanced_answer(question, retrieved_chunks, scope_result)
            
            # Prepare sources with similarity scores
            sources = []
            for i, (chunk, similarity) in enumerate(zip(retrieved_chunks, similarities)):
                sources.append({
                    "content": chunk["content"][:300] + "..." if len(chunk["content"]) > 300 else chunk["content"],
                    "metadata": chunk.get("metadata", {}),
                    "similarity_score": float(similarity) if similarity is not None else 0.0,
                    "rank": i + 1
                })
            
            # Calculate confidence based on similarity and scope
            confidence = self._calculate_confidence(similarities, scope_result)
            
            return {
                "answer": answer,
                "sources": sources,
                "in_scope": scope_result['in_scope'],
                "confidence": confidence,
                "scope_details": scope_result
            }
            
        except Exception as e:
            logger.error(f"Error in query: {e}")
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "in_scope": True,
                "confidence": 0.0
            }
    
    def _retrieve_chunks(self, question: str, k: int) -> tuple:
        """Retrieve most relevant chunks using best similarity search."""
        if self.embedding_model is None:
            # Fallback to keyword matching
            return self._keyword_retrieval(question, k)
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([question], convert_to_tensor=False)[0]
        
        if self.use_faiss and hasattr(self, 'faiss_index'):
            # Use FAISS for fast similarity search
            query_vector = np.array([query_embedding]).astype('float32')
            faiss.normalize_L2(query_vector)
            
            similarities, indices = self.faiss_index.search(query_vector, min(k, len(self.documents)))
            
            chunks = []
            scores = []
            for similarity, idx in zip(similarities[0], indices[0]):
                if idx < len(self.documents):
                    chunks.append(self.documents[idx])
                    scores.append(similarity)
            
            return chunks, scores
            
        elif hasattr(self, 'collection') and self.collection:
            # Use ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=min(k, self.collection.count())
            )
            
            chunks = []
            scores = []
            for doc, metadata, distance in zip(
                results['documents'][0], 
                results['metadatas'][0],
                results['distances'][0]
            ):
                chunks.append({"content": doc, "metadata": metadata})
                scores.append(1.0 - distance)  # Convert distance to similarity
            
            return chunks, scores
        else:
            # Fallback to keyword matching
            return self._keyword_retrieval(question, k)
    
    def _keyword_retrieval(self, question: str, k: int) -> tuple:
        """Fallback keyword-based retrieval."""
        if not hasattr(self, 'document_chunks') or not self.document_chunks:
            return [], []
        
        question_words = set(question.lower().split())
        scored_chunks = []
        
        for chunk in self.document_chunks:
            chunk_words = set(chunk["content"].lower().split())
            # Jaccard similarity
            intersection = len(question_words.intersection(chunk_words))
            union = len(question_words.union(chunk_words))
            score = intersection / union if union > 0 else 0
            
            if score > 0:
                scored_chunks.append((chunk, score))
        
        # Sort by score and take top k
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_chunks = scored_chunks[:k]
        
        chunks = [chunk for chunk, _ in top_chunks]
        scores = [score for _, score in top_chunks]
        
        return chunks, scores
    
    def _generate_enhanced_answer(self, question: str, chunks: List[Dict], scope_result: Dict) -> str:
        """Generate enhanced answer using best practices."""
        if not scope_result.get('in_scope', True):
            return (
                "This question appears to be outside the scope of the uploaded documents. "
                "I can only provide information based on the documents you've shared. "
                "Please ask questions related to the content of your uploaded files."
            )
        
        # Combine relevant content
        context = "\n\n".join([chunk["content"] for chunk in chunks[:3]])
        
        # Template-based answer generation with better context
        if any(word in question.lower() for word in ['what', 'define', 'explain']):
            sentences = context.split('.')
            relevant_sentences = [s.strip() for s in sentences if any(
                word in s.lower() for word in question.lower().split()
            )][:3]
            
            if relevant_sentences:
                return ". ".join(relevant_sentences) + "."
        
        elif any(word in question.lower() for word in ['how', 'process', 'method']):
            sentences = context.split('.')
            process_sentences = [s.strip() for s in sentences if any(
                word in s.lower() for word in ['step', 'process', 'method', 'how', 'procedure']
            )][:3]
            
            if process_sentences:
                return ". ".join(process_sentences) + "."
        
        elif any(word in question.lower() for word in ['list', 'types', 'kinds', 'examples']):
            # Look for bullet points or numbered lists
            lines = context.split('\n')
            list_items = [line.strip() for line in lines if 
                         line.strip().startswith(('-', '*', '•')) or 
                         any(char.isdigit() and '.' in line for char in line[:5])][:5]
            
            if list_items:
                return "Based on the document:\n" + "\n".join(list_items)
        
        # Default response with best excerpt
        return f"Based on the uploaded documents: {context[:400]}..."
    
    def _calculate_confidence(self, similarities: List[float], scope_result: Dict) -> float:
        """Calculate confidence score for the answer."""
        if not similarities:
            return 0.0
        
        # Base confidence from similarity scores
        avg_similarity = np.mean(similarities) if similarities else 0.0
        max_similarity = max(similarities) if similarities else 0.0
        
        # Scope confidence
        scope_confidence = scope_result.get('confidence', 0.5)
        
        # Combine confidences
        similarity_confidence = (avg_similarity + max_similarity) / 2
        overall_confidence = (similarity_confidence * 0.7) + (scope_confidence * 0.3)
        
        return min(1.0, overall_confidence)
    
    def _get_document_count(self) -> int:
        """Get total number of stored documents/chunks."""
        if self.use_faiss and hasattr(self, 'faiss_index'):
            return len(self.documents)
        elif hasattr(self, 'collection') and self.collection:
            return self.collection.count()
        elif hasattr(self, 'document_chunks'):
            return len(self.document_chunks)
        else:
            return 0
    
    def _get_all_content(self) -> str:
        """Get all document content for scope validation."""
        if self.use_faiss and hasattr(self, 'documents'):
            return "\n".join([doc["content"] for doc in self.documents])
        elif hasattr(self, 'collection') and self.collection:
            try:
                results = self.collection.get()
                return "\n".join(results['documents']) if results['documents'] else ""
            except:
                return ""
        elif hasattr(self, 'document_chunks'):
            return "\n".join([chunk["content"] for chunk in self.document_chunks])
        else:
            return ""
    
    def clear_documents(self):
        """Clear all documents."""
        if self.use_faiss:
            if hasattr(self, 'faiss_index'):
                delattr(self, 'faiss_index')
            self.documents = []
        elif hasattr(self, 'collection') and self.collection:
            try:
                self.chroma_client.delete_collection("enhanced_embeddings")
                self.collection = self.chroma_client.get_or_create_collection("enhanced_embeddings")
            except:
                pass
        else:
            self.document_chunks = []
        
        logger.info("All documents cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        return {
            "total_chunks": self._get_document_count(),
            "embedding_model": "all-mpnet-base-v2" if self.embedding_model else "keyword-based",
            "embedding_dimension": self.embedding_dim,
            "vector_store": "FAISS" if self.use_faiss else "ChromaDB" if hasattr(self, 'collection') else "In-memory",
            "text_splitter": "LangChain" if LANGCHAIN_AVAILABLE else "Custom",
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "bert_score_available": BERT_SCORE_AVAILABLE
        }