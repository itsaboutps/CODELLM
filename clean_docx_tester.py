"""
Comprehensive DOCX Testing Framework - Clean Implementation
Direct testing of DOCX files with proper RAG integration
"""

import os
import sys
import json
import time
import docx
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import backend components
try:
    from backend.rag_engine import RAGEngine
    from backend.scope_validator import ScopeValidator
    from backend.text_chunker import AdvancedTextChunker
    print("✅ Backend components imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def main():
    """Run comprehensive DOCX testing"""
    print("🚀 Comprehensive DOCX Testing Framework")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Test files
    test_files = {
        'urban_green_spaces': 'Title_ The Global Impact of Urban Green Spaces.docx',
        'electric_vehicles': 'Title_ The Rise of Electric Vehicles and the Future of Transportation.docx'
    }
    
    # Test questions from TESTME.md
    test_questions = {
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
                "What differences exist between early and modern motivations for preserving green spaces?"
            ],
            'out_of_scope': [
                "What year was the Paris Climate Agreement signed?",
                "Who is the current mayor of Singapore?",
                "What is the population of New York City?"
            ]
        },
        'electric_vehicles': {
            'factual_recall': [
                "When did the first practical electric car appear?",
                "What was Tesla's first electric car model, and when was it launched?",
                "How many miles could the Tesla Roadster travel on a single charge?"
            ],
            'contextual_comparative': [
                "How did the popularity of EVs change from the 1920s to the 21st century?",
                "Compare the technological barriers of early EVs with modern challenges."
            ],
            'out_of_scope': [
                "What is the range of the Tesla Model S Plaid?",
                "Who is the current CEO of Tesla?",
                "When was the Paris Agreement signed?"
            ]
        }
    }
    
    def extract_docx_content(file_path: str) -> Optional[str]:
        """Extract text content from DOCX file"""
        try:
            doc = docx.Document(file_path)
            content_parts = []
            
            for paragraph in doc.paragraphs:
                text = paragraph.text.strip()
                if text:
                    content_parts.append(text)
            
            full_content = '\n\n'.join(content_parts)
            logger.info(f"Extracted {len(full_content)} characters from {file_path}")
            return full_content
        except Exception as e:
            logger.error(f"Error extracting DOCX content: {e}")
            return None
    
    def create_rag_with_content(content: str, doc_name: str) -> Optional[RAGEngine]:
        """Create RAG engine and add content"""
        try:
            rag_engine = RAGEngine()
            chunker = AdvancedTextChunker()
            chunks = chunker.chunk_text(content)
            
            if hasattr(rag_engine, 'collection') and rag_engine.collection:
                chunk_texts = [chunk.content for chunk in chunks]
                chunk_ids = [f"{doc_name}_chunk_{i}" for i in range(len(chunks))]
                chunk_metadatas = [{"source": doc_name, "chunk_id": i} for i in range(len(chunks))]
                
                rag_engine.collection.add(
                    documents=chunk_texts,
                    ids=chunk_ids,
                    metadatas=chunk_metadatas
                )
                
                logger.info(f"Added {len(chunks)} chunks to RAG for {doc_name}")
            
            return rag_engine
        except Exception as e:
            logger.error(f"Error creating RAG: {e}")
            return None
    
    def test_question(rag_engine: RAGEngine, question: str, expected_scope: str) -> Dict:
        """Test a single question"""
        try:
            start_time = time.time()
            response = rag_engine.query(question)
            processing_time = time.time() - start_time
            
            if isinstance(response, dict):
                answer = response.get('answer', '')
                in_scope = response.get('in_scope', True)
            else:
                answer = str(response)
                in_scope = answer != "I don't have information about that in the uploaded documents."
            
            # Evaluate correctness
            if expected_scope == 'out_of_scope':
                correct = not in_scope or "don't have information" in answer.lower()
            else:
                correct = in_scope and "don't have information" not in answer.lower()
            
            return {
                'question': question,
                'answer': answer[:200] + "..." if len(answer) > 200 else answer,
                'in_scope': in_scope,
                'expected_scope': expected_scope,
                'correct': correct,
                'processing_time': processing_time
            }
        except Exception as e:
            return {
                'question': question,
                'error': str(e),
                'correct': False,
                'processing_time': 0
            }
    
    # Main testing loop
    total_tests = 0
    total_passed = 0
    results = {}
    
    for doc_key, file_path in test_files.items():
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
        
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {doc_key.replace('_', ' ').title()}")
        print(f"📄 File: {file_path}")
        print(f"{'='*60}")
        
        # Extract content
        content = extract_docx_content(file_path)
        if not content:
            print(f"❌ Failed to extract content from {file_path}")
            continue
        
        print(f"📋 Extracted {len(content)} characters")
        
        # Create RAG engine
        rag_engine = create_rag_with_content(content, doc_key)
        if not rag_engine:
            print(f"❌ Failed to create RAG engine for {doc_key}")
            continue
        
        print(f"⚙️ RAG engine initialized")
        
        # Test questions for this document
        doc_questions = test_questions.get(doc_key, {})
        doc_results = {}
        doc_total = 0
        doc_passed = 0
        
        for category, question_list in doc_questions.items():
            print(f"\n📊 Testing {category.replace('_', ' ').title()} ({len(question_list)} questions)")
            
            category_results = []
            expected_scope = 'out_of_scope' if category == 'out_of_scope' else 'positive'
            
            for i, question in enumerate(question_list, 1):
                print(f"  {i:2d}. {question[:60]}{'...' if len(question) > 60 else ''}")
                
                result = test_question(rag_engine, question, expected_scope)
                category_results.append(result)
                
                doc_total += 1
                total_tests += 1
                
                if result['correct']:
                    doc_passed += 1
                    total_passed += 1
                    print(f"      ✅ PASS")
                else:
                    print(f"      ❌ FAIL")
                
                time.sleep(0.05)  # Brief pause
            
            doc_results[category] = category_results
            
            # Category summary
            cat_passed = sum(1 for r in category_results if r['correct'])
            cat_rate = (cat_passed / len(category_results) * 100) if category_results else 0
            print(f"  📈 {category.replace('_', ' ').title()}: {cat_rate:.1f}% ({cat_passed}/{len(category_results)})")
        
        # Document summary
        doc_rate = (doc_passed / doc_total * 100) if doc_total > 0 else 0
        print(f"\n📋 {doc_key.replace('_', ' ').title()} Summary: {doc_rate:.1f}% ({doc_passed}/{doc_total})")
        
        results[doc_key] = {
            'file_path': file_path,
            'content_length': len(content),
            'total_questions': doc_total,
            'passed': doc_passed,
            'pass_rate': doc_rate,
            'category_results': doc_results
        }
    
    # Final summary
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE TEST RESULTS")
    print(f"{'='*80}")
    
    overall_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n🎯 Overall Performance:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_tests - total_passed}")
    print(f"   Pass Rate: {overall_rate:.1f}%")
    
    print(f"\n📚 Document Performance:")
    for doc_key, result in results.items():
        doc_name = doc_key.replace('_', ' ').title()
        print(f"   {doc_name}: {result['pass_rate']:.1f}% ({result['passed']}/{result['total_questions']})")
    
    # Analysis
    print(f"\n💡 Analysis:")
    if overall_rate >= 80:
        print("   ✅ Excellent performance! System handles DOCX content very well.")
    elif overall_rate >= 60:
        print("   ⚠️ Good performance with room for improvement.")
    else:
        print("   ❌ Performance needs significant improvement.")
        print("   🔧 Consider improving scope validation and content retrieval.")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"docx_test_results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'test_info': {
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': total_tests,
                    'passed': total_passed,
                    'pass_rate': overall_rate
                },
                'results': results
            }, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")

if __name__ == "__main__":
    main()