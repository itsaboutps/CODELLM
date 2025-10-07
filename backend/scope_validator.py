"""
Scope Validator - Determines if queries are within document scope

Validates whether user questions are related to the uploaded documents
using semantic similarity and keyword analysis to prevent out-of-scope responses.
"""

import logging
from typing import Dict, Any, List, Optional
import re

logger = logging.getLogger(__name__)

class ScopeValidator:
    """
    Validates whether user queries are within the scope of uploaded documents.
    
    Uses multiple validation strategies:
    1. Semantic similarity with document content
    2. Keyword overlap analysis
    3. Question type classification
    4. Context relevance scoring
    """
    
    def __init__(self, 
                 similarity_threshold: float = 0.3,
                 keyword_threshold: float = 0.1):
        """
        Initialize the scope validator.
        
        Args:
            similarity_threshold: Minimum similarity score for in-scope queries
            keyword_threshold: Minimum keyword overlap ratio for relevance
        """
        self.similarity_threshold = similarity_threshold
        self.keyword_threshold = keyword_threshold
        
        # Common out-of-scope question patterns
        self.out_of_scope_patterns = [
            r'\b(?:current|today|now|recent|latest|news|weather|time)\b',
            r'\b(?:recommend|suggest|advise|opinion|think|feel)\b.*(?:restaurant|movie|book|product)',
            r'\b(?:create|generate|make|build|develop)\b.*(?:code|program|app|website)',
            r'\b(?:personal|private|confidential|secret)\b.*(?:information|data|details)',
            r'\b(?:calculate|compute|solve)\b.*(?:math|equation|problem)',
            r'\b(?:translate|convert)\b.*(?:language|currency|unit)',
            r'\b(?:schedule|calendar|appointment|meeting|event)\b',
            r'\b(?:email|call|contact|phone|address)\b.*(?:someone|person|company)',
            r'\b(?:buy|purchase|order|shop|price|cost)\b.*(?:online|store|market)',
            r'\b(?:social media|facebook|twitter|instagram|linkedin)\b',
        ]
        
        # Question types that are typically document-related
        self.document_question_types = [
            r'\b(?:what|who|when|where|why|how)\b.*(?:document|text|content|chapter|section|page)',
            r'\b(?:explain|describe|define|summarize|outline)\b',
            r'\b(?:according to|based on|mentioned in|stated in|referenced in)\b',
            r'\b(?:find|locate|search|look for)\b.*(?:information|details|data|facts)',
            r'\b(?:key|main|important|significant|primary)\b.*(?:points|ideas|concepts|themes)',
        ]
        
        logger.info("Scope validator initialized")
    
    def validate_scope(self, query: str, collection_or_chunks) -> Dict[str, Any]:
        """
        Validate if a query is within the scope of uploaded documents.
        
        Args:
            query: User's question
            collection: ChromaDB collection containing document embeddings
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Initialize validation scores
            scores = {
                'pattern_score': 0.0,
                'semantic_score': 0.0,
                'keyword_score': 0.0,
                'question_type_score': 0.0
            }
            
            # 1. Pattern-based validation
            scores['pattern_score'] = self._check_patterns(query)
            
            # 2. Semantic similarity validation (if documents exist)
            document_count = self._get_document_count(collection_or_chunks)
            if document_count > 0:
                scores['semantic_score'] = self._check_semantic_similarity(query, collection_or_chunks)
            
            # 3. Keyword overlap validation
            if document_count > 0:
                scores['keyword_score'] = self._check_keyword_overlap(query, collection_or_chunks)
            
            # 4. Question type validation
            scores['question_type_score'] = self._check_question_type(query)
            
            # Calculate overall score
            weights = {
                'pattern_score': 0.3,
                'semantic_score': 0.4,
                'keyword_score': 0.2,
                'question_type_score': 0.1
            }
            
            overall_score = sum(scores[key] * weights[key] for key in scores)
            
            # Determine if query is in scope
            # Be more lenient when using fallback storage (keyword matching)
            if hasattr(collection_or_chunks, 'query'):
                # Using vector database - use stricter validation
                in_scope = overall_score >= 0.4 or (
                    scores['semantic_score'] >= self.similarity_threshold and
                    scores['keyword_score'] >= self.keyword_threshold
                )
            else:
                # Using fallback storage - be much more lenient to allow document questions
                in_scope = (overall_score >= 0.2 or 
                           scores['keyword_score'] >= 0.05 or 
                           scores['question_type_score'] >= 0.5 or
                           scores['pattern_score'] >= 0.6)
                
                # Additional check: if we have sources, it's likely in scope
                if document_count > 0 and scores.get('keyword_score', 0) > 0:
                    in_scope = True
            
            # Special case: if no documents, everything is out of scope
            if document_count == 0:
                in_scope = False
                overall_score = 0.0
            
            result = {
                'in_scope': in_scope,
                'overall_score': overall_score,
                'detailed_scores': scores,
                'confidence': min(overall_score * 2, 1.0),  # Convert to confidence score
                'reason': self._get_validation_reason(scores, in_scope)
            }
            
            logger.info(f"Scope validation: {in_scope} (score: {overall_score:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Error in scope validation: {e}")
            # Fallback: assume in scope if validation fails
            return {
                'in_scope': True,
                'overall_score': 0.5,
                'detailed_scores': {},
                'confidence': 0.5,
                'reason': 'Validation error - assuming in scope'
            }
    
    def _check_patterns(self, query: str) -> float:
        """
        Check if query matches out-of-scope patterns.
        
        Args:
            query: User's question
            
        Returns:
            Pattern score (0.0 = out of scope, 1.0 = in scope)
        """
        query_lower = query.lower()
        
        # Check for out-of-scope patterns
        out_of_scope_matches = 0
        for pattern in self.out_of_scope_patterns:
            if re.search(pattern, query_lower):
                out_of_scope_matches += 1
        
        # Check for document-related patterns
        document_matches = 0
        for pattern in self.document_question_types:
            if re.search(pattern, query_lower):
                document_matches += 1
        
        # Calculate pattern score
        if out_of_scope_matches > 0:
            return max(0.0, 0.5 - (out_of_scope_matches * 0.3))
        elif document_matches > 0:
            return min(1.0, 0.7 + (document_matches * 0.2))
        else:
            return 0.5  # Neutral score
    
    def _get_document_count(self, collection_or_chunks) -> int:
        """Get the number of documents/chunks available."""
        try:
            if hasattr(collection_or_chunks, 'count'):
                # ChromaDB collection
                return collection_or_chunks.count()
            elif isinstance(collection_or_chunks, list):
                # Simple list of chunks
                return len(collection_or_chunks)
            else:
                return 0
        except:
            return 0
    
    def _check_semantic_similarity(self, query: str, collection_or_chunks) -> float:
        """
        Check semantic similarity between query and document content.
        
        Args:
            query: User's question
            collection: ChromaDB collection
            
        Returns:
            Semantic similarity score (0.0-1.0)
        """
        try:
            # Handle different storage types
            if hasattr(collection_or_chunks, 'query'):
                # ChromaDB collection
                results = collection_or_chunks.query(
                    query_texts=[query],
                    n_results=min(5, collection_or_chunks.count())
                )
            else:
                # Simple list - do keyword matching
                return self._simple_keyword_similarity(query, collection_or_chunks)
            
            if not results['documents'][0]:
                return 0.0
            
            # Simple similarity based on query results
            # If we get results, there's some semantic similarity
            distances = results.get('distances', [[]])[0]
            
            if distances:
                # Convert distance to similarity (assuming cosine distance)
                # Smaller distance = higher similarity
                avg_distance = sum(distances) / len(distances)
                similarity = max(0.0, 1.0 - avg_distance)
                return min(1.0, similarity)
            
            return 0.5  # Default similarity if no distances available
            
        except Exception as e:
            logger.warning(f"Error in semantic similarity check: {e}")
            return 0.5
    
    def _simple_keyword_similarity(self, query: str, chunks: list) -> float:
        """Simple keyword similarity for fallback."""
        query_words = set(word.lower() for word in query.split() if len(word) > 2)
        if not query_words or not chunks:
            return 0.0
        
        max_similarity = 0.0
        total_matches = 0
        
        for chunk in chunks[:10]:  # Check more chunks
            chunk_text = chunk.get('content', '').lower()
            
            # Count direct word matches
            matches = sum(1 for word in query_words if word in chunk_text)
            if matches > 0:
                similarity = matches / len(query_words)
                max_similarity = max(max_similarity, similarity)
                total_matches += matches
        
        # Boost score if we have many matches across chunks
        avg_similarity = total_matches / (len(chunks) * len(query_words)) if chunks and query_words else 0
        
        return max(max_similarity, avg_similarity * 2)  # Give some boost for distributed matches
    
    def _check_keyword_overlap(self, query: str, collection_or_chunks) -> float:
        """
        Check keyword overlap between query and document content.
        
        Args:
            query: User's question
            collection: ChromaDB collection
            
        Returns:
            Keyword overlap score (0.0-1.0)
        """
        try:
            # Extract keywords from query
            query_keywords = self._extract_keywords(query)
            
            if not query_keywords:
                return 0.5
            
            # Get a sample of document content
            if hasattr(collection_or_chunks, 'query'):
                # ChromaDB collection
                results = collection_or_chunks.query(
                    query_texts=[query],
                    n_results=min(10, collection_or_chunks.count())
                )
                
                if not results['documents'][0]:
                    return 0.0
                
                # Combine document texts
                document_text = ' '.join(results['documents'][0]).lower()
            else:
                # Simple list
                if not collection_or_chunks:
                    return 0.0
                document_text = ' '.join([chunk.get('content', '') for chunk in collection_or_chunks[:10]]).lower()
            
            document_keywords = self._extract_keywords(document_text)
            
            # Calculate overlap
            if not document_keywords or not query_keywords:
                # Fallback: simple substring matching
                matches = sum(1 for word in query_keywords if word in document_text.lower())
                return min(1.0, matches / len(query_keywords) if query_keywords else 0)
            
            overlap = len(query_keywords.intersection(document_keywords))
            total_query_keywords = len(query_keywords)
            
            overlap_ratio = overlap / total_query_keywords if total_query_keywords > 0 else 0.0
            
            # Be more generous with matching
            if overlap_ratio > 0.1:  # If we have some matches
                return min(1.0, overlap_ratio * 1.5)
            
            return overlap_ratio
            
        except Exception as e:
            logger.warning(f"Error in keyword overlap check: {e}")
            return 0.5
    
    def _check_question_type(self, query: str) -> float:
        """
        Analyze the type of question to determine document relevance.
        
        Args:
            query: User's question
            
        Returns:
            Question type score (0.0-1.0)
        """
        query_lower = query.lower()
        
        # Document-specific question indicators
        document_indicators = [
            'document', 'text', 'content', 'chapter', 'section', 'page',
            'author', 'written', 'mentions', 'states', 'describes',
            'according to', 'based on', 'referenced', 'cited', 'report',
            'findings', 'data', 'research', 'study', 'analysis', 'evidence'
        ]
        
        # Generic knowledge question indicators
        generic_indicators = [
            'generally', 'typically', 'usually', 'in general',
            'worldwide', 'globally', 'universally', 'commonly known',
            'scientific fact', 'mathematical', 'historical event'
        ]
        
        # Count indicators
        document_score = sum(1 for indicator in document_indicators if indicator in query_lower)
        generic_score = sum(1 for indicator in generic_indicators if indicator in query_lower)
        
        # Question words that suggest document-specific queries
        specific_question_words = ['what does', 'how does', 'why does', 'when does', 'where does']
        specific_score = sum(1 for word in specific_question_words if word in query_lower)
        
        # Calculate final score
        if document_score > 0 or specific_score > 0:
            return min(1.0, 0.7 + ((document_score + specific_score) * 0.1))
        elif generic_score > 0:
            return max(0.0, 0.3 - (generic_score * 0.1))
        else:
            return 0.5
    
    def _extract_keywords(self, text: str) -> set:
        """
        Extract meaningful keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            Set of keywords
        """
        # Simple keyword extraction
        # Remove common stop words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'what', 'when', 'where', 'why', 'how', 'which', 'who', 'whom'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out stop words and short words
        keywords = {word for word in words if word not in stop_words and len(word) >= 3}
        
        return keywords
    
    def _get_validation_reason(self, scores: Dict[str, float], in_scope: bool) -> str:
        """
        Generate a human-readable reason for the validation result.
        
        Args:
            scores: Detailed validation scores
            in_scope: Whether query is in scope
            
        Returns:
            Validation reason string
        """
        if in_scope:
            if scores.get('semantic_score', 0) > 0.5:
                return "Query appears to be related to document content based on semantic similarity"
            elif scores.get('keyword_score', 0) > 0.3:
                return "Query contains keywords found in the uploaded documents"
            elif scores.get('question_type_score', 0) > 0.6:
                return "Query appears to be asking about document-specific content"
            else:
                return "Query is likely within document scope"
        else:
            if scores.get('pattern_score', 0) < 0.3:
                return "Query matches patterns typically outside document scope"
            elif scores.get('semantic_score', 0) < 0.2:
                return "Query has low semantic similarity to document content"
            elif scores.get('keyword_score', 0) < 0.1:
                return "Query contains few keywords found in the documents"
            else:
                return "Query appears to be outside the scope of uploaded documents"
    
    def get_scope_suggestions(self, query: str) -> List[str]:
        """
        Get suggestions for reformulating out-of-scope queries.
        
        Args:
            query: User's question
            
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        query_lower = query.lower()
        
        # Generic suggestions based on query patterns
        if any(word in query_lower for word in ['recommend', 'suggest', 'advise']):
            suggestions.append("Try asking about recommendations or suggestions mentioned in your documents")
        
        if any(word in query_lower for word in ['current', 'today', 'recent', 'latest']):
            suggestions.append("Ask about information that might be contained in your uploaded documents")
        
        if any(word in query_lower for word in ['create', 'generate', 'make', 'build']):
            suggestions.append("Ask about processes or methods described in your documents")
        
        # Default suggestions
        if not suggestions:
            suggestions.extend([
                "Try asking about specific topics mentioned in your documents",
                "Ask for explanations or summaries of content from your uploaded files",
                "Request information that might be found in your document collection"
            ])
        
        return suggestions[:3]  # Limit to 3 suggestions