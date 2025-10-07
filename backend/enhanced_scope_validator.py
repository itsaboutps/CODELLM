"""
Enhanced Scope Validator using Best Free Models

Uses BERT-Score, spaCy NLP, and advanced semantic analysis
for accurate scope validation.
"""

import logging
from typing import Dict, Any, List, Optional
import re

# Best Free NLP Models
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from bert_score import score as bert_score
    BERT_SCORE_AVAILABLE = True
except ImportError:
    BERT_SCORE_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class EnhancedScopeValidator:
    """
    Enhanced scope validator using state-of-the-art free models:
    - BERT-Score for semantic similarity
    - spaCy for advanced NLP analysis  
    - Named Entity Recognition
    - Advanced question classification
    """
    
    def __init__(self, similarity_threshold: float = 0.4, confidence_threshold: float = 0.6):
        self.similarity_threshold = similarity_threshold
        self.confidence_threshold = confidence_threshold
        
        # Initialize spaCy model
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                # Try to load English model
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("✅ spaCy English model loaded")
            except OSError:
                logger.warning("spaCy English model not found. Run: python -m spacy download en_core_web_sm")
        
        # Initialize sentence transformer for backup
        self.sentence_model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("✅ Backup sentence transformer loaded")
            except:
                pass
        
        # Enhanced patterns for better detection
        self.document_indicators = {
            'strong': [
                r'\b(?:according to|based on|mentioned in|stated in|referenced in|cited in)\b',
                r'\b(?:the document|this text|the paper|the report|the article)\b',
                r'\b(?:chapter|section|page|paragraph|appendix)\b',
                r'\b(?:author|writer|researcher) (?:says|states|mentions|argues)\b'
            ],
            'medium': [
                r'\b(?:what|who|when|where|why|how) (?:does|is|are|did|was|were)\b',
                r'\b(?:explain|describe|define|summarize|outline|clarify)\b',
                r'\b(?:key|main|important|significant|primary|central) (?:points|ideas|concepts|themes|findings)\b',
                r'\b(?:find|locate|search|look for) (?:information|details|data|facts)\b'
            ],
            'weak': [
                r'\b(?:tell me about|information about|details about)\b',
                r'\b(?:understand|know|learn) (?:about|more)\b'
            ]
        }
        
        self.out_of_scope_patterns = {
            'strong': [
                r'\b(?:current|today|now|recent|latest|breaking|live) (?:news|weather|events|updates)\b',
                r'\b(?:create|generate|make|build|develop|write|code|program)\b',
                r'\b(?:buy|purchase|order|shop|price|cost|sell|market)\b',
                r'\b(?:personal|private|my|your) (?:opinion|advice|recommendation)\b',
                r'\b(?:call|email|contact|phone|text|message) (?:someone|person|company)\b'
            ],
            'medium': [
                r'\b(?:recommend|suggest|advise) (?:me|a|an|some)\b',
                r'\b(?:best|better|worse|comparison) (?:than|between|among)\b',
                r'\b(?:calculate|compute|solve|math|equation|formula)\b',
                r'\b(?:translate|convert) (?:to|from|into)\b'
            ]
        }
        
        logger.info("Enhanced Scope Validator initialized")
    
    def validate_scope(self, query: str, document_content: str) -> Dict[str, Any]:
        """Enhanced scope validation using multiple advanced methods."""
        try:
            scores = {
                'bert_score': 0.0,
                'semantic_score': 0.0, 
                'pattern_score': 0.0,
                'entity_score': 0.0,
                'question_type_score': 0.0,
                'keyword_score': 0.0
            }
            
            # 1. BERT-Score semantic similarity (best method)
            if BERT_SCORE_AVAILABLE and document_content:
                scores['bert_score'] = self._bert_similarity(query, document_content)
            
            # 2. Sentence transformer similarity (backup)
            if self.sentence_model and document_content:
                scores['semantic_score'] = self._sentence_similarity(query, document_content)
            
            # 3. Enhanced pattern matching
            scores['pattern_score'] = self._enhanced_pattern_matching(query)
            
            # 4. Named Entity Recognition
            if self.nlp:
                scores['entity_score'] = self._entity_overlap(query, document_content)
            
            # 5. Question type classification
            scores['question_type_score'] = self._classify_question_type(query)
            
            # 6. Advanced keyword matching
            scores['keyword_score'] = self._advanced_keyword_matching(query, document_content)
            
            # Calculate weighted overall score
            weights = {
                'bert_score': 0.3,
                'semantic_score': 0.25,
                'pattern_score': 0.15,
                'entity_score': 0.1,
                'question_type_score': 0.1,
                'keyword_score': 0.1
            }
            
            overall_score = sum(scores[key] * weights[key] for key in scores if scores[key] is not None)
            
            # Enhanced decision logic
            in_scope = self._make_scope_decision(scores, overall_score)
            confidence = self._calculate_confidence(scores, overall_score)
            
            return {
                'in_scope': in_scope,
                'overall_score': overall_score,
                'confidence': confidence,
                'detailed_scores': scores,
                'reason': self._generate_reason(scores, in_scope),
                'suggestions': self._generate_suggestions(query, in_scope) if not in_scope else []
            }
            
        except Exception as e:
            logger.error(f"Enhanced scope validation error: {e}")
            # Fallback to permissive validation
            return {
                'in_scope': True,
                'overall_score': 0.5,
                'confidence': 0.5,
                'detailed_scores': {},
                'reason': 'Validation error - assuming in scope',
                'suggestions': []
            }
    
    def _bert_similarity(self, query: str, document_content: str) -> float:
        """Use BERT-Score for semantic similarity (most accurate)."""
        try:
            # Sample document content to avoid memory issues
            doc_sample = document_content[:2000] if len(document_content) > 2000 else document_content
            
            # Calculate BERT-Score
            P, R, F1 = bert_score([query], [doc_sample], lang="en", verbose=False)
            
            # Return F1 score as similarity
            return float(F1.mean().item())
            
        except Exception as e:
            logger.debug(f"BERT-Score error: {e}")
            return 0.0
    
    def _sentence_similarity(self, query: str, document_content: str) -> float:
        """Backup similarity using sentence transformers."""
        try:
            # Sample content
            doc_sample = document_content[:1000] if len(document_content) > 1000 else document_content
            
            # Get embeddings
            query_emb = self.sentence_model.encode([query])
            doc_emb = self.sentence_model.encode([doc_sample])
            
            # Calculate cosine similarity
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(query_emb, doc_emb)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.debug(f"Sentence similarity error: {e}")
            return 0.0
    
    def _enhanced_pattern_matching(self, query: str) -> float:
        """Enhanced pattern matching with weighted scores."""
        query_lower = query.lower()
        
        # Check document indicators (positive patterns)
        doc_score = 0.0
        for strength, patterns in self.document_indicators.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    if strength == 'strong':
                        doc_score += 0.4
                    elif strength == 'medium':
                        doc_score += 0.25
                    else:  # weak
                        doc_score += 0.1
        
        # Check out-of-scope patterns (negative patterns)
        oos_score = 0.0
        for strength, patterns in self.out_of_scope_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    if strength == 'strong':
                        oos_score += 0.5
                    else:  # medium
                        oos_score += 0.3
        
        # Combine scores
        final_score = max(0.0, doc_score - oos_score)
        return min(1.0, final_score)
    
    def _entity_overlap(self, query: str, document_content: str) -> float:
        """Calculate entity overlap using spaCy NER."""
        try:
            # Extract entities from query
            query_doc = self.nlp(query)
            query_entities = {ent.text.lower() for ent in query_doc.ents}
            
            if not query_entities:
                return 0.5  # Neutral if no entities in query
            
            # Extract entities from document (sample)
            doc_sample = document_content[:2000] if len(document_content) > 2000 else document_content
            doc_doc = self.nlp(doc_sample)
            doc_entities = {ent.text.lower() for ent in doc_doc.ents}
            
            if not doc_entities:
                return 0.3  # Lower score if no entities in document
            
            # Calculate entity overlap
            overlap = len(query_entities.intersection(doc_entities))
            total = len(query_entities.union(doc_entities))
            
            return overlap / total if total > 0 else 0.0
            
        except Exception as e:
            logger.debug(f"Entity overlap error: {e}")
            return 0.5
    
    def _classify_question_type(self, query: str) -> float:
        """Classify question type and return relevance score."""
        query_lower = query.lower().strip()
        
        # Document-specific question types (high score)
        if any(phrase in query_lower for phrase in [
            'what does the document say', 'according to the text',
            'in this document', 'the author mentions',
            'what is stated', 'what is written'
        ]):
            return 0.9
        
        # Information-seeking questions (medium-high score)
        if query_lower.startswith(('what', 'who', 'when', 'where', 'why', 'how')):
            # Check if it's asking about specific information
            if any(word in query_lower for word in [
                'explain', 'describe', 'define', 'summarize', 'list', 'identify'
            ]):
                return 0.7
            return 0.6
        
        # Imperative requests (medium score)
        if query_lower.startswith(('explain', 'describe', 'define', 'list', 'show', 'tell')):
            return 0.6
        
        # General knowledge questions (lower score)
        if any(phrase in query_lower for phrase in [
            'in general', 'typically', 'usually', 'commonly',
            'what is', 'tell me about', 'I want to know'
        ]):
            return 0.4
        
        # Commands/requests outside document scope (very low score)
        if query_lower.startswith(('create', 'generate', 'make', 'build', 'write')):
            return 0.1
        
        return 0.5  # Neutral for unclear questions
    
    def _advanced_keyword_matching(self, query: str, document_content: str) -> float:
        """Advanced keyword matching with NLP preprocessing."""
        if not document_content:
            return 0.0
        
        try:
            # Use spaCy for better tokenization if available
            if self.nlp:
                query_doc = self.nlp(query.lower())
                doc_doc = self.nlp(document_content.lower()[:2000])  # Sample for performance
                
                # Extract meaningful tokens (exclude stop words, punctuation)
                query_tokens = {token.lemma_ for token in query_doc 
                              if not token.is_stop and not token.is_punct and len(token.text) > 2}
                doc_tokens = {token.lemma_ for token in doc_doc 
                            if not token.is_stop and not token.is_punct and len(token.text) > 2}
            else:
                # Fallback to simple tokenization
                stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
                query_tokens = {word for word in query.lower().split() if len(word) > 2 and word not in stop_words}
                doc_tokens = {word for word in document_content.lower()[:2000].split() if len(word) > 2 and word not in stop_words}
            
            if not query_tokens:
                return 0.0
            
            # Calculate overlap
            intersection = len(query_tokens.intersection(doc_tokens))
            union = len(query_tokens.union(doc_tokens))
            
            jaccard_score = intersection / union if union > 0 else 0.0
            
            # Boost score if many query terms found
            coverage = intersection / len(query_tokens) if query_tokens else 0.0
            
            return (jaccard_score + coverage) / 2
            
        except Exception as e:
            logger.debug(f"Advanced keyword matching error: {e}")
            return 0.0
    
    def _make_scope_decision(self, scores: Dict[str, float], overall_score: float) -> bool:
        """Enhanced decision making using multiple criteria."""
        
        # Strong positive indicators
        if scores.get('bert_score', 0) > 0.6:
            return True
        
        if scores.get('pattern_score', 0) > 0.7:
            return True
        
        # Strong negative indicators  
        if scores.get('pattern_score', 0) < 0.1 and overall_score < 0.2:
            return False
        
        # Multiple moderate indicators
        moderate_scores = [
            scores.get('semantic_score', 0),
            scores.get('entity_score', 0),
            scores.get('keyword_score', 0)
        ]
        
        if sum(1 for score in moderate_scores if score > 0.4) >= 2:
            return True
        
        # Overall threshold with bias toward inclusion
        return overall_score > 0.3  # Lower threshold for better user experience
    
    def _calculate_confidence(self, scores: Dict[str, float], overall_score: float) -> float:
        """Calculate confidence in the scope decision."""
        
        # High confidence indicators
        if scores.get('bert_score', 0) > 0.7:
            return 0.9
        
        if scores.get('pattern_score', 0) > 0.8:
            return 0.85
        
        # Confidence based on score consistency
        non_zero_scores = [score for score in scores.values() if score > 0.1]
        
        if len(non_zero_scores) >= 3:
            variance = max(non_zero_scores) - min(non_zero_scores)
            consistency = 1.0 - min(1.0, variance)
            return min(0.95, overall_score + consistency * 0.3)
        
        # Default confidence based on overall score
        return min(0.8, overall_score + 0.2)
    
    def _generate_reason(self, scores: Dict[str, float], in_scope: bool) -> str:
        """Generate human-readable reason for the decision."""
        
        if in_scope:
            if scores.get('bert_score', 0) > 0.5:
                return "High semantic similarity to document content detected"
            elif scores.get('pattern_score', 0) > 0.6:
                return "Question patterns indicate document-specific inquiry"
            elif scores.get('keyword_score', 0) > 0.4:
                return "Significant keyword overlap with document content"
            else:
                return "Question appears to be within document scope"
        else:
            if scores.get('pattern_score', 0) < 0.2:
                return "Question patterns suggest non-document inquiry"
            elif all(score < 0.3 for score in scores.values()):
                return "Low similarity to document content across all metrics"
            else:
                return "Question appears to be outside document scope"
    
    def _generate_suggestions(self, query: str, in_scope: bool) -> List[str]:
        """Generate helpful suggestions for improving queries."""
        
        if in_scope:
            return []
        
        suggestions = []
        
        # Analyze query to provide specific suggestions
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['weather', 'news', 'current']):
            suggestions.append("Try asking about information that might be contained in your uploaded documents")
        
        if any(word in query_lower for word in ['recommend', 'suggest', 'best']):
            suggestions.append("Ask about recommendations or comparisons mentioned in your documents")
        
        if any(word in query_lower for word in ['create', 'make', 'generate']):
            suggestions.append("Ask about processes, methods, or instructions described in your documents")
        
        # Default suggestions
        if not suggestions:
            suggestions.extend([
                "Try asking about specific topics mentioned in your documents",
                "Use phrases like 'According to the document...' or 'What does the text say about...'",
                "Ask for explanations, summaries, or definitions from your uploaded content"
            ])
        
        return suggestions[:3]  # Limit to 3 suggestions