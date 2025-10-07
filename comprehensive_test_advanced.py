"""
Comprehensive End-to-End Testing for Document Assistant RAG

This script implements comprehensive testing with 20 positive, 20 negative, 
and 20 complex questions across multiple test documents to validate 
the RAG system's performance and scope validation.
"""

import json
import sys
import os
from pathlib import Path
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import components with fallback
try:
    from backend.enhanced_rag_engine import EnhancedRAGEngine as RAGEngine
    enhanced_rag = True
    print("✨ Using enhanced RAG engine for testing")
except ImportError as e:
    print(f"⚠️ Enhanced RAG not available ({e}), using basic version")
    from backend.rag_engine import RAGEngine
    enhanced_rag = False

try:
    from backend.enhanced_scope_validator import EnhancedScopeValidator as ScopeValidator
    enhanced_scope = True
    print("✨ Using enhanced scope validator for testing")
except ImportError as e:
    print(f"⚠️ Enhanced scope validator not available ({e}), using basic version")
    from backend.scope_validator import ScopeValidator
    enhanced_scope = False

enhanced_mode = enhanced_rag and enhanced_scope

from backend.document_processor import DocumentProcessor

class ComprehensiveRAGTester:
    """Comprehensive testing suite for Document Assistant RAG"""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.rag_engine = RAGEngine()
        self.scope_validator = ScopeValidator()
        self.results = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'enhanced_mode': enhanced_mode,
                'total_tests': 0,
                'passed': 0,
                'failed': 0
            },
            'document_tests': {},
            'overall_metrics': {}
        }
        
    def load_test_documents(self):
        """Load all test documents"""
        test_docs_dir = Path("test_documents")
        documents = {}
        
        for doc_file in test_docs_dir.glob("*.md"):
            print(f"Loading document: {doc_file.name}")
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Process document - create a mock uploaded file
                class MockUploadedFile:
                    def __init__(self, content, name):
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
                
                text_file = MockUploadedFile(content, doc_file.name)
                
                # Add document to RAG engine
                success = self.rag_engine.add_document(text_file)
                
                if success:
                    documents[doc_file.stem] = {
                        'file_path': str(doc_file),
                        'content_length': len(content),
                        'loaded_successfully': True
                    }
                    print(f"✅ Loaded {doc_file.stem}: {len(content)} characters")
                else:
                    print(f"❌ Failed to load {doc_file.stem}")
                
            except Exception as e:
                print(f"❌ Error loading {doc_file.name}: {e}")
                
        return documents
    
    def get_test_questions(self):
        """Define comprehensive test questions for each document"""
        
        # Climate Report Questions
        climate_questions = {
            'positive': [
                "What are the main causes of climate change mentioned in the document?",
                "How do greenhouse gases affect global temperature?",
                "What is the impact of deforestation on carbon dioxide levels?",
                "What renewable energy sources are discussed?",
                "How does ocean acidification relate to climate change?",
                "What are the projected temperature increases by 2100?",
                "How do carbon emissions from transportation contribute to climate change?",
                "What role do fossil fuels play in global warming?",
                "How does methane from agriculture affect the climate?",
                "What are the effects of climate change on sea levels?",
                "How do solar panels help reduce carbon emissions?",
                "What is the relationship between industrial emissions and climate change?",
                "How does urban heat island effect contribute to warming?",
                "What are the impacts of climate change on biodiversity?",
                "How do carbon sinks help mitigate climate change?",
                "What role does the Paris Agreement play in climate action?",
                "How does energy efficiency help combat climate change?",
                "What are the economic impacts of climate change mentioned?",
                "How do extreme weather events relate to climate change?",
                "What adaptation strategies are discussed for climate change?"
            ],
            'negative': [
                "What is the best recipe for chocolate cake?",
                "How do I fix a broken computer?",
                "What are the latest stock market trends?",
                "How to train a dog effectively?",
                "What is the capital of Australia?",
                "How to write a Python function?",
                "What are the side effects of aspirin?",
                "How to change a car tire?",
                "What is quantum computing?",
                "How to learn Spanish quickly?",
                "What are the rules of chess?",
                "How to grow tomatoes in a garden?",
                "What is the history of the Roman Empire?",
                "How to bake bread at home?",
                "What are the symptoms of flu?",
                "How to play guitar chords?",
                "What is machine learning algorithm?",
                "How to paint a room?",
                "What are the benefits of yoga?",
                "How to start a business?"
            ],
            'complex': [
                "How do the climate impacts discussed relate to machine learning applications?",
                "Can artificial intelligence help solve the climate issues mentioned here?",
                "What programming languages would be best for climate modeling?",
                "How does climate change affect software development practices?",
                "What database technologies are mentioned for climate data?",
                "How do climate scientists use Python for their research?",
                "What role does blockchain play in carbon credit systems mentioned?",
                "How can mobile apps help with climate change mitigation strategies discussed?",
                "What cybersecurity concerns exist for climate monitoring systems?",
                "How does cloud computing relate to the energy consumption issues mentioned?",
                "What data visualization techniques are best for climate data presented here?",
                "How do IoT sensors contribute to the climate monitoring discussed?",
                "What role does big data analytics play in climate predictions mentioned?",
                "How can virtual reality be used to educate about climate impacts discussed?",
                "What network protocols are used in climate monitoring systems?",
                "How does edge computing relate to renewable energy systems mentioned?",
                "What APIs are available for accessing climate data discussed here?",
                "How can containerization help with climate modeling applications?",
                "What DevOps practices are relevant to climate research workflows?",
                "How does microservices architecture apply to climate monitoring systems?"
            ]
        }
        
        # Machine Learning Guide Questions
        ml_questions = {
            'positive': [
                "What are the main types of machine learning algorithms discussed?",
                "How does supervised learning differ from unsupervised learning?",
                "What is the purpose of feature engineering in machine learning?",
                "How do neural networks process information?",
                "What is overfitting and how can it be prevented?",
                "How does gradient descent optimization work?",
                "What are the applications of deep learning mentioned?",
                "How do you evaluate machine learning model performance?",
                "What is the role of training data in machine learning?",
                "How do convolutional neural networks work for image processing?",
                "What is cross-validation and why is it important?",
                "How does regularization help in machine learning?",
                "What are ensemble methods in machine learning?",
                "How do decision trees make predictions?",
                "What is the bias-variance tradeoff?",
                "How does backpropagation work in neural networks?",
                "What preprocessing steps are important for machine learning?",
                "How do support vector machines classify data?",
                "What is transfer learning and when is it useful?",
                "How do you handle imbalanced datasets in machine learning?"
            ],
            'negative': [
                "What is the best way to cook pasta?",
                "How do I change my car's oil?",
                "What are the symptoms of a cold?",
                "How to plant a garden?",
                "What is the weather forecast for tomorrow?",
                "How to learn French grammar?",
                "What are the rules of basketball?",
                "How to fix a leaky faucet?",
                "What is the history of ancient Egypt?",
                "How to knit a scarf?",
                "What are the benefits of meditation?",
                "How to bake a birthday cake?",
                "What is constitutional law?",
                "How to train for a marathon?",
                "What are the phases of the moon?",
                "How to write a business plan?",
                "What is organic chemistry?",
                "How to play the piano?",
                "What are greenhouse gas emissions?",
                "How to manage personal finances?"
            ],
            'complex': [
                "How do machine learning techniques apply to climate change research?",
                "What role does ML play in renewable energy optimization mentioned in climate documents?",
                "How can deep learning help with climate prediction models?",
                "What machine learning algorithms are best for analyzing investment portfolios?",
                "How does natural language processing relate to financial document analysis?",
                "Can neural networks predict stock market trends based on climate data?",
                "How do recommendation systems apply to sustainable investment strategies?",
                "What role does computer vision play in monitoring deforestation mentioned in climate reports?",
                "How can reinforcement learning optimize carbon trading strategies?",
                "What machine learning techniques help with ESG investment analysis?",
                "How do clustering algorithms segment climate-conscious investors?",
                "What deep learning models predict climate impact on financial markets?",
                "How does time series analysis apply to both climate data and financial trends?",
                "What role does anomaly detection play in climate monitoring and fraud detection?",
                "How can machine learning optimize renewable energy investment portfolios?",
                "What natural language processing techniques analyze climate policy documents?",
                "How do ensemble methods combine climate and financial prediction models?",
                "What role does federated learning play in distributed climate research?",
                "How can graph neural networks model climate-finance relationships?",
                "What machine learning techniques optimize carbon offset investment strategies?"
            ]
        }
        
        # Investment Report Questions
        investment_questions = {
            'positive': [
                "What are the key investment strategies discussed in the document?",
                "How is portfolio diversification explained?",
                "What risk management techniques are mentioned?",
                "How do you calculate return on investment?",
                "What are the different asset classes covered?",
                "How does dollar-cost averaging work?",
                "What is the importance of asset allocation?",
                "How do market volatility and risk relate?",
                "What are the benefits of long-term investing?",
                "How do dividend-paying stocks generate income?",
                "What is the role of bonds in a portfolio?",
                "How do you assess investment risk tolerance?",
                "What are the tax implications of different investments?",
                "How does compound interest benefit long-term investors?",
                "What are the characteristics of growth vs value investing?",
                "How do mutual funds and ETFs work?",
                "What is the importance of emergency funds?",
                "How do you rebalance an investment portfolio?",
                "What factors affect stock market performance?",
                "How does inflation impact investment returns?"
            ],
            'negative': [
                "How do I bake chocolate chip cookies?",
                "What is the best way to learn guitar?",
                "How do plants perform photosynthesis?",
                "What are the rules of soccer?",
                "How to fix a flat tire?",
                "What is the capital of Canada?",
                "How to write a resume?",
                "What are the symptoms of diabetes?",
                "How to train a puppy?",
                "What is quantum physics?",
                "How to grow vegetables?",
                "What is the history of jazz music?",
                "How to paint with watercolors?",
                "What are the benefits of exercise?",
                "How to learn meditation?",
                "What is cellular biology?",
                "How to change a light bulb?",
                "What are the phases of sleep?",
                "How to make homemade pizza?",
                "What is ancient Greek philosophy?"
            ],
            'complex': [
                "How do investment strategies relate to machine learning model selection?",
                "What role does algorithmic trading play in the investment approaches discussed?",
                "How can artificial intelligence optimize the portfolio strategies mentioned?",
                "What machine learning techniques predict market trends discussed here?",
                "How do robo-advisors implement the investment principles mentioned?",
                "What role does big data play in the risk assessment strategies discussed?",
                "How can blockchain technology enhance the investment processes mentioned?",
                "What programming languages are best for implementing the trading strategies discussed?",
                "How do neural networks model the market volatility patterns mentioned?",
                "What role does natural language processing play in analyzing financial news for investments?",
                "How can reinforcement learning optimize the asset allocation strategies discussed?",
                "What data mining techniques extract insights from the investment data mentioned?",
                "How do sentiment analysis algorithms affect the market psychology discussed?",
                "What role does computer vision play in technical analysis mentioned?",
                "How can distributed computing handle the big data investment analysis discussed?",
                "What API integrations are needed for the investment platforms mentioned?",
                "How does cloud computing scale the investment analysis tools discussed?",
                "What cybersecurity measures protect the investment strategies mentioned?",
                "How can IoT data influence the investment decisions discussed?",
                "What role does edge computing play in real-time trading systems mentioned?"
            ]
        }
        
        # Architecture Patterns Questions
        architecture_questions = {
            'positive': [
                "What are the main categories of design patterns discussed?",
                "How does the Singleton pattern ensure single instance creation?",
                "What is the purpose of the Factory Method pattern?",
                "How does the Observer pattern implement event-driven architecture?",
                "What are the benefits of the MVC architectural pattern?",
                "How does the Repository pattern abstract data access?",
                "What is the role of the Adapter pattern in system integration?",
                "How does the Strategy pattern encapsulate algorithms?",
                "What are the key principles of microservices patterns?",
                "How does the Circuit Breaker pattern prevent cascading failures?",
                "What is dependency injection and its benefits?",
                "How do caching patterns improve application performance?",
                "What are the different types of test doubles mentioned?",
                "How does the Decorator pattern add functionality dynamically?",
                "What is the Command pattern and its use cases?",
                "How does the Facade pattern simplify complex interfaces?",
                "What are the security patterns for authentication?",
                "How does connection pooling optimize database access?",
                "What anti-patterns should be avoided in software design?",
                "How does the Saga pattern manage distributed transactions?"
            ],
            'negative': [
                "What is the best recipe for apple pie?",
                "How do you care for houseplants?",
                "What are the rules of tennis?",
                "How to change car brakes?",
                "What is the geography of South America?",
                "How to learn swimming techniques?",
                "What are the benefits of running?",
                "How to write poetry?",
                "What is the history of World War II?",
                "How to make homemade bread?",
                "What are the symptoms of allergies?",
                "How to play chess strategies?",
                "What is marine biology?",
                "How to garden organically?",
                "What are different art movements?",
                "How to cook Thai cuisine?",
                "What is classical music theory?",
                "How to learn photography?",
                "What are climate zones?",
                "How to practice yoga poses?"
            ],
            'complex': [
                "How do the design patterns apply to climate monitoring systems architecture?",
                "What patterns are best for implementing machine learning model deployment?",
                "How do microservices patterns support financial trading platform scalability?",
                "What design patterns optimize investment portfolio analysis systems?",
                "How does the Observer pattern monitor climate data streams in real-time?",
                "What architectural patterns support ML model versioning and deployment?",
                "How do caching patterns improve performance in financial data analysis?",
                "What security patterns protect sensitive climate research data?",
                "How does the Repository pattern abstract climate data storage systems?",
                "What patterns enable scalable machine learning training pipelines?",
                "How do messaging patterns coordinate distributed climate simulations?",
                "What design patterns optimize high-frequency trading system performance?",
                "How does the Circuit Breaker pattern protect ML inference services?",
                "What patterns manage configuration in multi-environment ML deployments?",
                "How do behavioral patterns coordinate climate model ensemble predictions?",
                "What architectural patterns support real-time investment decision engines?",
                "How does the Strategy pattern select optimal climate prediction algorithms?",
                "What patterns enable fault-tolerant financial risk calculation systems?",
                "How do structural patterns organize complex ML feature engineering pipelines?",
                "What design patterns optimize carbon footprint calculation microservices?"
            ]
        }
        
        return {
            'climate_report': climate_questions,
            'ml_guide': ml_questions,
            'investment_report': investment_questions,
            'architecture_patterns': architecture_questions
        }
    
    def test_question(self, document_id, question, expected_scope, question_type):
        """Test a single question and return results"""
        start_time = time.time()
        
        try:
            # Get answer from RAG engine
            answer = self.rag_engine.query(question, document_id)
            
            # Validate scope
            is_in_scope = self.scope_validator.validate_scope(
                question, 
                answer if answer != "I don't have information about that in the uploaded documents." else ""
            )
            
            processing_time = time.time() - start_time
            
            # Determine if test passed
            if expected_scope == "positive":
                passed = (is_in_scope and answer != "I don't have information about that in the uploaded documents.")
            elif expected_scope == "negative":
                passed = (not is_in_scope or answer == "I don't have information about that in the uploaded documents.")
            else:  # complex
                # For complex questions, we expect nuanced handling
                passed = (answer != "I don't have information about that in the uploaded documents.")
            
            result = {
                'question': question,
                'expected_scope': expected_scope,
                'question_type': question_type,
                'answer': answer[:500] + "..." if len(answer) > 500 else answer,
                'is_in_scope': is_in_scope,
                'passed': passed,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                'question': question,
                'expected_scope': expected_scope,
                'question_type': question_type,
                'answer': f"Error: {str(e)}",
                'is_in_scope': False,
                'passed': False,
                'processing_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def run_comprehensive_tests(self):
        """Run all comprehensive tests"""
        print("\n" + "="*60)
        print("🧪 Starting Comprehensive RAG Testing Suite")
        print("="*60)
        
        # Load documents
        print("\n📁 Loading test documents...")
        documents = self.load_test_documents()
        
        # Get test questions
        print("\n📝 Preparing test questions...")
        all_questions = self.get_test_questions()
        
        # Run tests for each document
        for doc_id, questions in all_questions.items():
            if doc_id not in documents:
                print(f"⚠️ Document {doc_id} not found, skipping tests")
                continue
                
            print(f"\n🔍 Testing document: {doc_id}")
            print("-" * 40)
            
            doc_results = {
                'positive_tests': [],
                'negative_tests': [],
                'complex_tests': [],
                'summary': {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'pass_rate': 0.0
                }
            }
            
            # Test each category
            for category, question_list in questions.items():
                print(f"\n  📊 Testing {category} questions ({len(question_list)} questions)...")
                
                for i, question in enumerate(question_list, 1):
                    print(f"    Question {i}/{len(question_list)}: ", end="")
                    result = self.test_question(doc_id, question, category, f"{category}_{i}")
                    
                    if result['passed']:
                        print("✅ PASS")
                    else:
                        print("❌ FAIL")
                    
                    doc_results[f"{category}_tests"].append(result)
                    doc_results['summary']['total'] += 1
                    
                    if result['passed']:
                        doc_results['summary']['passed'] += 1
                        self.results['test_info']['passed'] += 1
                    else:
                        doc_results['summary']['failed'] += 1
                        self.results['test_info']['failed'] += 1
                    
                    self.results['test_info']['total_tests'] += 1
            
            # Calculate pass rate for document
            if doc_results['summary']['total'] > 0:
                doc_results['summary']['pass_rate'] = (
                    doc_results['summary']['passed'] / doc_results['summary']['total']
                ) * 100
            
            self.results['document_tests'][doc_id] = doc_results
            
            print(f"\n  📈 {doc_id} Summary:")
            print(f"    Total: {doc_results['summary']['total']}")
            print(f"    Passed: {doc_results['summary']['passed']}")
            print(f"    Failed: {doc_results['summary']['failed']}")
            print(f"    Pass Rate: {doc_results['summary']['pass_rate']:.1f}%")
        
        # Calculate overall metrics
        self.calculate_overall_metrics()
        
        # Print final summary
        self.print_final_summary()
        
        # Save results
        self.save_results()
    
    def calculate_overall_metrics(self):
        """Calculate overall performance metrics"""
        total_tests = self.results['test_info']['total_tests']
        total_passed = self.results['test_info']['passed']
        
        if total_tests > 0:
            overall_pass_rate = (total_passed / total_tests) * 100
        else:
            overall_pass_rate = 0.0
        
        # Calculate per-category metrics
        positive_total = positive_passed = 0
        negative_total = negative_passed = 0
        complex_total = complex_passed = 0
        
        for doc_id, doc_results in self.results['document_tests'].items():
            for test in doc_results['positive_tests']:
                positive_total += 1
                if test['passed']:
                    positive_passed += 1
            
            for test in doc_results['negative_tests']:
                negative_total += 1
                if test['passed']:
                    negative_passed += 1
            
            for test in doc_results['complex_tests']:
                complex_total += 1
                if test['passed']:
                    complex_passed += 1
        
        self.results['overall_metrics'] = {
            'total_tests': total_tests,
            'total_passed': total_passed,
            'total_failed': total_tests - total_passed,
            'overall_pass_rate': overall_pass_rate,
            'positive_pass_rate': (positive_passed / positive_total * 100) if positive_total > 0 else 0,
            'negative_pass_rate': (negative_passed / negative_total * 100) if negative_total > 0 else 0,
            'complex_pass_rate': (complex_passed / complex_total * 100) if complex_total > 0 else 0,
            'category_breakdown': {
                'positive': {'total': positive_total, 'passed': positive_passed},
                'negative': {'total': negative_total, 'passed': negative_passed},
                'complex': {'total': complex_total, 'passed': complex_passed}
            }
        }
    
    def print_final_summary(self):
        """Print comprehensive final summary"""
        print("\n" + "="*60)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("="*60)
        
        metrics = self.results['overall_metrics']
        
        print(f"\n🎯 Overall Performance:")
        print(f"   Total Tests: {metrics['total_tests']}")
        print(f"   Passed: {metrics['total_passed']}")
        print(f"   Failed: {metrics['total_failed']}")
        print(f"   Overall Pass Rate: {metrics['overall_pass_rate']:.1f}%")
        
        print(f"\n📋 Category Breakdown:")
        print(f"   Positive Questions: {metrics['positive_pass_rate']:.1f}% pass rate")
        print(f"   Negative Questions: {metrics['negative_pass_rate']:.1f}% pass rate")
        print(f"   Complex Questions: {metrics['complex_pass_rate']:.1f}% pass rate")
        
        print(f"\n📚 Document Performance:")
        for doc_id, doc_results in self.results['document_tests'].items():
            summary = doc_results['summary']
            print(f"   {doc_id}: {summary['pass_rate']:.1f}% ({summary['passed']}/{summary['total']})")
        
        print(f"\n⚙️ System Info:")
        print(f"   Enhanced Mode: {'✅ Yes' if enhanced_mode else '❌ No'}")
        print(f"   Test Duration: {datetime.now().isoformat()}")
        
        # Performance recommendations
        print(f"\n💡 Recommendations:")
        if metrics['overall_pass_rate'] >= 80:
            print("   ✅ Excellent performance! System is working well.")
        elif metrics['overall_pass_rate'] >= 60:
            print("   ⚠️ Good performance with room for improvement.")
        else:
            print("   ❌ Performance needs attention. Consider model tuning.")
            
        if metrics['negative_pass_rate'] < 70:
            print("   🔍 Scope validation may need improvement.")
            
        if metrics['complex_pass_rate'] < 50:
            print("   🧠 Complex question handling needs enhancement.")
    
    def save_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving results: {e}")

def main():
    """Run comprehensive testing"""
    tester = ComprehensiveRAGTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()