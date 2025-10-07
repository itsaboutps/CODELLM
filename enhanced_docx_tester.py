"""
Enhanced DOCX Testing Framework with Direct RAG Integration
Addresses RAG engine collection issues and improves document retrieval
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import re

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import document processing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    logger.warning("python-docx not available. Install with: pip install python-docx")
    DOCX_AVAILABLE = False

# Import backend components with fallback
try:
    from backend.rag_engine import RAGEngine
    from backend.scope_validator import ScopeValidator
    enhanced_mode = False
    print("🔧 Using basic RAG engine and scope validator")
except ImportError as e:
    print(f"❌ Cannot import basic components: {e}")
    sys.exit(1)

from backend.document_processor import DocumentProcessor

class EnhancedDOCXTester:
    """Enhanced tester for DOCX files with specific question validation"""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.results = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'enhanced_mode': enhanced_mode,
                'total_tests': 0,
                'passed': 0,
                'failed': 0
            },
            'document_tests': {},
            'detailed_results': {}
        }
        
        # Test questions from TESTME.md
        self.test_questions = self._load_test_questions_from_testme()
        
    def _load_test_questions_from_testme(self) -> Dict[str, Dict]:
        """Load test questions from TESTME.md file"""
        return {
            'urban_green_spaces': {
                'factual_recall': [
                    "Who designed Central Park in New York?",
                    "In what year was Central Park completed?",
                    "Which cities are named as global leaders in green urban planning?",
                    "How much can trees reduce urban temperatures by?",
                    "What is the United Nations' goal that supports sustainable cities?"
                ],
                'contextual_comparative': [
                    "How did the purpose of green spaces change from the 19th to the 21st century?",
                    "What differences exist between early and modern motivations for preserving green spaces?",
                    "How are modern technologies contributing to green space management?",
                    "What role did the environmental movements of the 1970s and 1980s play in shaping urban policy?"
                ],
                'analytical_reasoning': [
                    'Why is "green gentrification" considered a challenge in urban development?',
                    "How can equitable access to green spaces promote community well-being?",
                    "Why did Frederick Law Olmsted advocate for nature in urban environments?",
                    "How do green spaces contribute to combating climate change in cities?"
                ],
                'summarization': [
                    "Summarize the evolution of urban green spaces from the 19th century to today.",
                    "What are the key benefits and challenges of green spaces in modern cities?",
                    "Explain how sustainability and social equity intersect in the context of urban green spaces."
                ],
                'out_of_scope': [
                    "What year was the Paris Climate Agreement signed?",
                    "Who is the current mayor of Singapore?",
                    "What is the population of New York City?",
                    "Which company created GIS software?"
                ]
            },
            'electric_vehicles': {
                'factual_recall': [
                    "When did the first practical electric car appear?",
                    "What was Tesla's first electric car model, and when was it launched?",
                    "How many miles could the Tesla Roadster travel on a single charge?",
                    "In what year did global EV sales exceed 3 million annually?",
                    "Which United Nations goal supports climate action related to transport?",
                    "What percentage of new car sales are expected to be electric by 2035?"
                ],
                'contextual_comparative': [
                    "How did the popularity of EVs change from the 1920s to the 21st century?",
                    "Compare the technological barriers of early EVs with modern challenges.",
                    "What regions of the world have contributed to accelerating EV adoption?",
                    "How are governments addressing environmental concerns in battery production?"
                ],
                'analytical_reasoning': [
                    "Why did gasoline cars surpass early electric vehicles in the 20th century?",
                    "How do charging innovations aim to make EV use more convenient?",
                    "Why are lithium and nickel central to EV sustainability discussions?",
                    "How does integrating renewable energy with EVs enhance environmental impact?"
                ],
                'summarization': [
                    "Summarize the evolution of electric vehicles from their invention to 2035 projections.",
                    "What are the key environmental benefits and challenges associated with EVs?",
                    "Describe how technology and policy together influence the growth of electric transportation."
                ],
                'out_of_scope': [
                    "What is the range of the Tesla Model S Plaid?",
                    "Who is the current CEO of Tesla?",
                    "What country produces the most crude oil?",
                    "When was the Paris Agreement signed?"
                ]
            }
        }
    
    def extract_docx_content(self, file_path: str) -> Optional[str]:
        """Extract text content from DOCX file"""
        if not DOCX_AVAILABLE:
            logger.error("python-docx not available for DOCX processing")
            return None
            
        try:
            doc = docx.Document(file_path)
            content = []
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    content.append(text)
            
            full_content = '\n\n'.join(content)
            logger.info(f"Extracted {len(full_content)} characters from {file_path}")
            return full_content
            
        except Exception as e:
            logger.error(f"Error extracting DOCX content from {file_path}: {e}")
            return None
    
    def load_docx_document(self, file_path: str, doc_key: str) -> bool:
        """Load a DOCX document into a new RAG engine instance"""
        try:
            print(f"📄 Loading {file_path}...")
            
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
            
            # Extract DOCX content
            content = self.extract_docx_content(file_path)
            if not content:
                print(f"❌ Failed to extract content from {file_path}")
                return False
            
            # Create new RAG engine instance for this document
            self.rag_engine = RAGEngine()
            
            # Create mock file object for the RAG engine
            class MockUploadedFile:
                def __init__(self, content: str, name: str):
                    self.content = content
                    self.name = name
                    self._position = 0
                
                def read(self, size=-1):
                    if size == -1:
                        result = self.content[self._position:]
                        self._position = len(self.content)
                    else:
                        result = self.content[self._position:self._position + size]
                        self._position += len(result)
                    return result.encode('utf-8') if isinstance(result, str) else result
                
                def seek(self, position):
                    self._position = position
            
            # Create mock file and add to RAG
            mock_file = MockUploadedFile(content, os.path.basename(file_path))
            success = self.rag_engine.add_document(mock_file)
            
            if success:
                print(f"✅ Successfully loaded {doc_key}")
                print(f"   Content length: {len(content)} characters")
                return True
            else:
                print(f"❌ Failed to load {doc_key} into RAG engine")
                return False
                
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")
            return False
    
    def test_single_question(self, question: str, expected_scope: str, category: str, doc_key: str) -> Dict:
        """Test a single question and evaluate the response"""
        start_time = time.time()
        
        try:
            # Get RAG response
            if hasattr(self.rag_engine, 'query'):
                if enhanced_mode:
                    # Enhanced RAG engine
                    response = self.rag_engine.query(question, doc_key)
                else:
                    # Basic RAG engine
                    response = self.rag_engine.query(question)
            else:
                raise AttributeError("RAG engine does not have query method")
            
            processing_time = time.time() - start_time
            
            # Handle different response formats
            if isinstance(response, dict):
                answer = response.get('answer', '')
                in_scope = response.get('in_scope', True)
                sources = response.get('sources', [])
            elif isinstance(response, str):
                answer = response
                in_scope = True if response != "I don't have information about that in the uploaded documents." else False
                sources = []
            else:
                answer = str(response)
                in_scope = True
                sources = []
            
            # Evaluate scope validation
            is_correct_scope = self._evaluate_scope_validation(in_scope, expected_scope, question)
            
            # Evaluate answer quality if in-scope
            answer_quality = self._evaluate_answer_quality(answer, expected_scope, question) if expected_scope != 'negative' else None
            
            # Determine if test passed
            if expected_scope == 'negative':
                # Out-of-scope questions should be rejected
                passed = not in_scope or answer == "I don't have information about that in the uploaded documents."
            else:
                # In-scope questions should be answered with quality content
                passed = in_scope and (answer_quality is None or answer_quality > 0.3)
            
            return {
                'question': question,
                'category': category,
                'expected_scope': expected_scope,
                'response': {
                    'answer': answer[:500] + "..." if len(answer) > 500 else answer,
                    'in_scope': in_scope,
                    'sources_count': len(sources) if sources else 0
                },
                'evaluation': {
                    'scope_correct': is_correct_scope,
                    'answer_quality': answer_quality,
                    'processing_time': processing_time
                },
                'passed': passed,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error testing question '{question}': {e}")
            return {
                'question': question,
                'category': category,
                'expected_scope': expected_scope,
                'error': str(e),
                'passed': False,
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
    
    def _evaluate_scope_validation(self, actual_scope: bool, expected_scope: str, question: str) -> bool:
        """Evaluate if scope validation is correct"""
        if expected_scope == 'negative' or expected_scope == 'out_of_scope':
            # Out-of-scope questions should return False
            return not actual_scope
        else:
            # In-scope questions should return True
            return actual_scope
    
    def _evaluate_answer_quality(self, answer: str, expected_scope: str, question: str) -> float:
        """Evaluate answer quality for in-scope questions"""
        if not answer:
            return 0.0
        
        answer_lower = answer.lower()
        
        # Check for error messages
        error_indicators = [
            'error', 'slice indices', 'exception', 'failed',
            'cannot process', 'processing error'
        ]
        if any(indicator in answer_lower for indicator in error_indicators):
            return 0.0
        
        # Check for generic non-answers
        generic_responses = [
            "i don't have information",
            "i don't have enough information",
            "outside the scope",
            "can't find information",
            "not found in the document",
            "no information available"
        ]
        
        if any(generic in answer_lower for generic in generic_responses):
            return 0.1
        
        # Basic quality scoring
        score = 0.0
        
        # Has substantial content (not just rejection)
        if len(answer) > 30:
            score += 0.3
        
        # Contains relevant keywords from question
        question_words = set(re.findall(r'\b\w+\b', question.lower()))
        answer_words = set(re.findall(r'\b\w+\b', answer_lower))
        common_words = question_words.intersection(answer_words)
        if len(common_words) > 1:
            score += 0.3
        
        # Appears to be informative (contains numbers, names, or specific terms)
        if re.search(r'\b\d{4}\b|\b[A-Z][a-z]+\s+[A-Z][a-z]+\b|\b\d+%\b', answer):
            score += 0.4
        
        return min(score, 1.0)
    
    def test_document(self, doc_key: str, file_path: str) -> Dict:
        """Test a single document with all its questions"""
        print(f"\n{'='*80}")
        print(f"🧪 Testing Document: {doc_key.replace('_', ' ').title()}")
        print(f"📄 File: {file_path}")
        print(f"{'='*80}")
        
        # Load document
        if not self.load_docx_document(file_path, doc_key):
            return {'error': f'Failed to load {file_path}'}
        
        # Get questions for this document
        if doc_key not in self.test_questions:
            return {'error': f'No test questions found for {doc_key}'}
        
        questions = self.test_questions[doc_key]
        results = {
            'document_info': {
                'key': doc_key,
                'file_path': file_path,
                'loaded': True
            },
            'category_results': {},
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'pass_rate': 0.0
            }
        }
        
        # Test each category
        for category, question_list in questions.items():
            print(f"\n📊 Testing {category.replace('_', ' ').title()} ({len(question_list)} questions)...")
            
            category_results = []
            expected_scope = 'negative' if category == 'out_of_scope' else 'positive'
            
            for i, question in enumerate(question_list, 1):
                print(f"  Question {i}/{len(question_list)}: {question[:80]}{'...' if len(question) > 80 else ''}")
                
                result = self.test_single_question(question, expected_scope, category, doc_key)
                category_results.append(result)
                
                # Update counters
                results['summary']['total'] += 1
                self.results['test_info']['total_tests'] += 1
                
                if result['passed']:
                    results['summary']['passed'] += 1
                    self.results['test_info']['passed'] += 1
                    print(f"    ✅ PASS")
                else:
                    results['summary']['failed'] += 1
                    self.results['test_info']['failed'] += 1
                    print(f"    ❌ FAIL - {result.get('error', 'See details in results')}")
                
                # Brief delay to avoid overwhelming the system
                time.sleep(0.1)
            
            results['category_results'][category] = category_results
            
            # Print category summary
            cat_passed = sum(1 for r in category_results if r['passed'])
            cat_total = len(category_results)
            cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
            print(f"  📈 {category.replace('_', ' ').title()} Summary: {cat_rate:.1f}% ({cat_passed}/{cat_total})")
        
        # Calculate pass rate
        if results['summary']['total'] > 0:
            results['summary']['pass_rate'] = results['summary']['passed'] / results['summary']['total']
        
        return results
    
    def run_comprehensive_test(self) -> None:
        """Run comprehensive tests on both DOCX files"""
        print(f"\n🚀 Enhanced DOCX Testing Framework")
        print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⚙️ Enhanced Mode: {'✅ Yes' if enhanced_mode else '❌ No'}")
        print("="*80)
        
        # Define test files
        test_files = {
            'urban_green_spaces': 'Title_ The Global Impact of Urban Green Spaces.docx',
            'electric_vehicles': 'Title_ The Rise of Electric Vehicles and the Future of Transportation.docx'
        }
        
        # Test each document
        for doc_key, file_path in test_files.items():
            result = self.test_document(doc_key, file_path)
            self.results['document_tests'][doc_key] = result
        
        # Print final summary
        self.print_final_summary()
        
        # Save results
        self.save_results()
        
        # Provide recommendations
        self.provide_recommendations()
    
    def print_final_summary(self) -> None:
        """Print comprehensive test summary"""
        print(f"\n{'='*80}")
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print(f"{'='*80}")
        
        total = self.results['test_info']['total_tests']
        passed = self.results['test_info']['passed']
        failed = self.results['test_info']['failed']
        overall_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n🎯 Overall Performance:")
        print(f"   Total Tests: {total}")
        print(f"   Passed: {passed}")
        print(f"   Failed: {failed}")
        print(f"   Pass Rate: {overall_rate:.1f}%")
        
        print(f"\n📚 Document Performance:")
        for doc_key, result in self.results['document_tests'].items():
            if 'summary' in result and 'error' not in result:
                doc_rate = result['summary']['pass_rate'] * 100
                doc_name = doc_key.replace('_', ' ').title()
                print(f"   {doc_name}: {doc_rate:.1f}% ({result['summary']['passed']}/{result['summary']['total']})")
                
                # Category breakdown
                for category, cat_results in result['category_results'].items():
                    cat_passed = sum(1 for r in cat_results if r['passed'])
                    cat_total = len(cat_results)
                    cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
                    category_name = category.replace('_', ' ').title()
                    print(f"     {category_name}: {cat_rate:.1f}% ({cat_passed}/{cat_total})")
            elif 'error' in result:
                print(f"   {doc_key}: ❌ {result['error']}")
        
        print(f"\n⚙️ System Info:")
        print(f"   Enhanced Mode: {'✅ Yes' if enhanced_mode else '❌ No'}")
        print(f"   DOCX Processing: {'✅ Available' if DOCX_AVAILABLE else '❌ Not Available'}")
        print(f"   Test Duration: {datetime.now().isoformat()}")
    
    def provide_recommendations(self) -> None:
        """Provide recommendations based on test results"""
        total = self.results['test_info']['total_tests']
        passed = self.results['test_info']['passed']
        overall_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n💡 Recommendations:")
        
        if overall_rate >= 80:
            print("   ✅ Excellent performance! System is working well.")
        elif overall_rate >= 60:
            print("   ⚠️ Good performance with room for improvement.")
            print("   🔧 Consider tuning scope validation thresholds.")
        else:
            print("   ❌ Performance needs attention.")
            print("   🔧 Consider upgrading to enhanced models.")
            print("   🔧 Review scope validation logic.")
        
        # Analyze category-specific issues
        categories_with_issues = []
        for doc_key, result in self.results['document_tests'].items():
            if 'category_results' in result:
                for category, cat_results in result['category_results'].items():
                    cat_passed = sum(1 for r in cat_results if r['passed'])
                    cat_total = len(cat_results)
                    cat_rate = (cat_passed / cat_total * 100) if cat_total > 0 else 0
                    
                    if cat_rate < 50:
                        categories_with_issues.append(f"{category} in {doc_key}")
        
        if categories_with_issues:
            print("   🎯 Focus improvement on:")
            for issue in categories_with_issues:
                print(f"     - {issue}")
    
    def save_results(self) -> None:
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_docx_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")

def main():
    """Main function to run enhanced DOCX testing"""
    print("🎯 Enhanced DOCX Testing Framework for Document Assistant RAG")
    print("📋 Testing against questions from TESTME.md")
    
    # Check if DOCX files exist
    required_files = [
        'Title_ The Global Impact of Urban Green Spaces.docx',
        'Title_ The Rise of Electric Vehicles and the Future of Transportation.docx'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Required file not found: {file_path}")
            return
    
    if not DOCX_AVAILABLE:
        print("❌ python-docx not available. Installing...")
        os.system("pip install python-docx")
    
    # Run tests
    tester = EnhancedDOCXTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()