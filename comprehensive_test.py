"""
Comprehensive End-to-End Test Suite for Document Assistant RAG
Tests 60 different questions: 20 positive, 20 negative, 20 complex/edge cases

This test evaluates:
1. Correct answers to document-related questions (Positive)
2. Proper rejection of out-of-scope questions (Negative) 
3. Handling of complex, ambiguous, or edge case questions (Complex)
"""

import sys
import os
import json
from typing import Dict, List, Any
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.rag_engine import RAGEngine

class ComprehensiveRAGTester:
    def __init__(self):
        self.rag_engine = None
        self.test_results = []
        self.document_loaded = False
        
    def initialize_system(self):
        """Initialize the RAG system and load the demo document."""
        print("🔧 Initializing RAG System...")
        try:
            self.rag_engine = RAGEngine()
            
            # Load the climate report demo document
            demo_file = "demo_climate_report.md"
            if not os.path.exists(demo_file):
                print(f"❌ Demo document '{demo_file}' not found!")
                return False
            
            # Create mock file object
            with open(demo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            class MockFile:
                def __init__(self, content, name):
                    self.content = content
                    self.name = name
                    self.size = len(content.encode('utf-8'))
                    self.pos = 0
                
                def read(self):
                    return self.content.encode('utf-8')
                
                def seek(self, pos):
                    self.pos = pos
            
            mock_file = MockFile(content, demo_file)
            success = self.rag_engine.add_document(mock_file)
            
            if success:
                print(f"✅ Demo document loaded successfully ({len(content)} characters)")
                self.document_loaded = True
                return True
            else:
                print("❌ Failed to load demo document")
                return False
                
        except Exception as e:
            print(f"❌ Error initializing system: {e}")
            return False
    
    def get_test_questions(self) -> Dict[str, List[Dict]]:
        """Define comprehensive test questions across different categories."""
        
        test_questions = {
            "positive": [
                # Direct factual questions from the document
                {"q": "What is the global temperature increase since the pre-industrial era?", "expected_keywords": ["1.2°C", "temperature", "pre-industrial"]},
                {"q": "How much have sea levels risen since 1880?", "expected_keywords": ["23 cm", "sea level", "1880"]},
                {"q": "What percentage of greenhouse gas emissions comes from transportation?", "expected_keywords": ["29%", "transportation", "emissions"]},
                {"q": "How many species are threatened with extinction?", "expected_keywords": ["1 million", "species", "extinction"]},
                {"q": "What are the atmospheric CO2 levels in 2023?", "expected_keywords": ["421", "parts per million", "CO2"]},
                
                # Summary and explanation questions
                {"q": "What are the key findings about climate change?", "expected_keywords": ["temperature", "emissions", "biodiversity"]},
                {"q": "Describe the regional impacts in North America", "expected_keywords": ["wildfire", "drought", "hurricane"]},
                {"q": "What mitigation strategies are mentioned in the report?", "expected_keywords": ["renewable energy", "carbon capture", "policy"]},
                {"q": "Explain the economic implications of climate change", "expected_keywords": ["43 trillion", "costs", "adaptation"]},
                {"q": "What are the recommendations for immediate actions?", "expected_keywords": ["renewable energy", "carbon pricing", "reforestation"]},
                
                # Analytical questions
                {"q": "How has renewable energy capacity changed since 2015?", "expected_keywords": ["300%", "solar", "growth"]},
                {"q": "What role does AI play in climate solutions?", "expected_keywords": ["monitoring", "predictive", "85% accuracy"]},
                {"q": "What are the adaptation measures for infrastructure?", "expected_keywords": ["coastal protection", "300 billion", "resilience"]},
                {"q": "How do green bonds support climate action?", "expected_keywords": ["500 billion", "green bonds", "renewable energy"]},
                {"q": "What is the Paris Agreement's temperature target?", "expected_keywords": ["1.5°C", "Paris Agreement", "pre-industrial"]},
                
                # Comparative questions
                {"q": "Which region is warming fastest according to the report?", "expected_keywords": ["Arctic", "twice as fast"]},
                {"q": "What sector contributes most to greenhouse gas emissions?", "expected_keywords": ["transportation", "29%"]},
                {"q": "How do coral reefs show climate impact?", "expected_keywords": ["bleaching", "50%", "shallow-water"]},
                {"q": "What technology has seen the biggest cost decrease?", "expected_keywords": ["battery storage", "85%", "decrease"]},
                {"q": "Which time period is most crucial for climate action?", "expected_keywords": ["next decade", "window", "1.5°C"]}
            ],
            
            "negative": [
                # Current events not in document
                {"q": "What is today's weather forecast?", "should_reject": True},
                {"q": "Who won the latest election?", "should_reject": True},
                {"q": "What are the current stock market prices?", "should_reject": True},
                {"q": "What happened in the news yesterday?", "should_reject": True},
                {"q": "What is the latest COVID-19 update?", "should_reject": True},
                
                # Personal recommendations
                {"q": "What should I invest in for retirement?", "should_reject": True},
                {"q": "Which car should I buy?", "should_reject": True},
                {"q": "What restaurant do you recommend?", "should_reject": True},
                {"q": "Where should I go on vacation?", "should_reject": True},
                {"q": "What career path should I choose?", "should_reject": True},
                
                # Unrelated technical questions
                {"q": "How do I code a web application?", "should_reject": True},
                {"q": "What is the meaning of life?", "should_reject": True},
                {"q": "How do I solve this math problem: 2x + 5 = 15?", "should_reject": True},
                {"q": "What is the capital of France?", "should_reject": True},
                {"q": "How do I cook pasta?", "should_reject": True},
                
                # Entertainment and culture
                {"q": "Who is the best actor of all time?", "should_reject": True},
                {"q": "What is the plot of the latest Marvel movie?", "should_reject": True},
                {"q": "Who wrote the Harry Potter books?", "should_reject": True},
                {"q": "What is the best video game this year?", "should_reject": True},
                {"q": "Which music streaming service is better?", "should_reject": True}
            ],
            
            "complex": [
                # Ambiguous questions requiring interpretation
                {"q": "Is climate change real?", "type": "opinion_factual"},
                {"q": "What should governments do about climate change?", "type": "policy_interpretation"},
                {"q": "How accurate are climate predictions?", "type": "methodology_question"},
                {"q": "Why don't people believe in climate change?", "type": "psychological_social"},
                {"q": "Which climate solution is most effective?", "type": "comparative_judgment"},
                
                # Multi-part complex questions
                {"q": "Compare renewable energy growth with fossil fuel decline and predict future trends", "type": "multi_part_prediction"},
                {"q": "Analyze the relationship between economic costs and environmental benefits", "type": "relationship_analysis"},
                {"q": "Evaluate the feasibility of achieving net-zero by 2050 based on current progress", "type": "feasibility_assessment"},
                {"q": "What are the trade-offs between different climate mitigation strategies?", "type": "trade_off_analysis"},
                {"q": "How do regional impacts vary and what does this mean for global cooperation?", "type": "regional_global_synthesis"},
                
                # Edge cases and boundary testing
                {"q": "The report mentions AI accuracy of 85% - is this good or bad?", "type": "contextual_interpretation"},
                {"q": "Can geoengineering solve climate change completely?", "type": "limitation_assessment"},
                {"q": "What information is missing from this climate report?", "type": "gap_analysis"},
                {"q": "How reliable are the economic projections mentioned?", "type": "reliability_assessment"},
                {"q": "What would happen if all recommendations were implemented immediately?", "type": "scenario_analysis"},
                
                # Contradictory or challenging questions  
                {"q": "The report shows both progress and alarming trends - which is more significant?", "type": "contradiction_resolution"},
                {"q": "If renewable energy is growing so fast, why are emissions still rising?", "type": "apparent_contradiction"},
                {"q": "How can we trust climate models when weather forecasts are often wrong?", "type": "trust_credibility"},
                {"q": "Doesn't economic growth conflict with environmental protection?", "type": "fundamental_tension"},
                {"q": "Why should current generations pay for future climate impacts?", "type": "intergenerational_ethics"}
            ]
        }
        
        return test_questions
    
    def evaluate_response(self, question: str, response: Dict[str, Any], expected_data: Dict) -> Dict[str, Any]:
        """Evaluate the quality and appropriateness of a response."""
        
        evaluation = {
            "question": question,
            "answer": response.get("answer", ""),
            "in_scope": response.get("in_scope", False),
            "sources_count": len(response.get("sources", [])),
            "evaluation": {}
        }
        
        # Check if it's a rejection test
        if expected_data.get("should_reject", False):
            # For negative questions, we want the system to reject them
            if not response.get("in_scope", True):
                evaluation["evaluation"]["scope_handling"] = "✅ CORRECT - Properly rejected out-of-scope question"
                evaluation["evaluation"]["score"] = 1.0
            else:
                evaluation["evaluation"]["scope_handling"] = "❌ FAILED - Should have rejected out-of-scope question"
                evaluation["evaluation"]["score"] = 0.0
        else:
            # For positive/complex questions, evaluate content quality
            answer = response.get("answer", "").lower()
            expected_keywords = expected_data.get("expected_keywords", [])
            
            # Check keyword presence
            keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in answer)
            keyword_score = keyword_matches / len(expected_keywords) if expected_keywords else 0.5
            
            # Check if in scope
            scope_score = 1.0 if response.get("in_scope", False) else 0.0
            
            # Check sources
            sources_score = min(1.0, len(response.get("sources", [])) / 3)  # Expect at least 3 sources
            
            # Overall score
            overall_score = (keyword_score * 0.5 + scope_score * 0.3 + sources_score * 0.2)
            
            evaluation["evaluation"] = {
                "keyword_score": f"{keyword_score:.2f} ({keyword_matches}/{len(expected_keywords)} keywords found)",
                "scope_score": f"{scope_score:.2f} ({'In scope' if scope_score > 0 else 'Out of scope'})",
                "sources_score": f"{sources_score:.2f} ({len(response.get('sources', []))} sources)",
                "overall_score": f"{overall_score:.2f}",
                "score": overall_score
            }
            
            if overall_score >= 0.7:
                evaluation["evaluation"]["status"] = "✅ EXCELLENT"
            elif overall_score >= 0.5:
                evaluation["evaluation"]["status"] = "⚠️ ACCEPTABLE"
            else:
                evaluation["evaluation"]["status"] = "❌ POOR"
        
        return evaluation
    
    def run_test_category(self, category_name: str, questions: List[Dict]) -> List[Dict]:
        """Run tests for a specific category of questions."""
        print(f"\n🧪 Testing {category_name.upper()} Questions ({len(questions)} questions)")
        print("=" * 60)
        
        results = []
        
        for i, q_data in enumerate(questions, 1):
            question = q_data["q"]
            print(f"\n📝 Question {i}: {question}")
            
            try:
                # Get response from RAG system
                response = self.rag_engine.query(question)
                
                # Evaluate the response
                evaluation = self.evaluate_response(question, response, q_data)
                results.append(evaluation)
                
                # Print results
                print(f"💡 Answer: {response['answer'][:100]}{'...' if len(response['answer']) > 100 else ''}")
                print(f"🔍 In Scope: {response['in_scope']}")
                print(f"📚 Sources: {len(response['sources'])} found")
                
                if "score" in evaluation["evaluation"]:
                    print(f"⭐ Score: {evaluation['evaluation']['score']:.2f}")
                    if "status" in evaluation["evaluation"]:
                        print(f"📊 Status: {evaluation['evaluation']['status']}")
                
            except Exception as e:
                print(f"❌ Error processing question: {e}")
                results.append({
                    "question": question,
                    "error": str(e),
                    "evaluation": {"score": 0.0, "status": "❌ ERROR"}
                })
        
        return results
    
    def generate_summary_report(self, all_results: Dict[str, List]) -> Dict:
        """Generate a comprehensive summary report."""
        
        summary = {
            "test_timestamp": datetime.now().isoformat(),
            "categories": {},
            "overall": {}
        }
        
        total_questions = 0
        total_score = 0.0
        
        for category, results in all_results.items():
            scores = [r["evaluation"].get("score", 0.0) for r in results if "evaluation" in r]
            category_score = sum(scores) / len(scores) if scores else 0.0
            
            summary["categories"][category] = {
                "question_count": len(results),
                "average_score": category_score,
                "passed": sum(1 for s in scores if s >= 0.5),
                "failed": sum(1 for s in scores if s < 0.5),
                "pass_rate": (sum(1 for s in scores if s >= 0.5) / len(scores) * 100) if scores else 0
            }
            
            total_questions += len(results)
            total_score += category_score * len(results)
        
        overall_score = total_score / total_questions if total_questions > 0 else 0.0
        
        summary["overall"] = {
            "total_questions": total_questions,
            "overall_score": overall_score,
            "system_status": "✅ EXCELLENT" if overall_score >= 0.7 else "⚠️ ACCEPTABLE" if overall_score >= 0.5 else "❌ NEEDS IMPROVEMENT"
        }
        
        return summary
    
    def run_comprehensive_test(self):
        """Run the complete test suite."""
        print("🚀 Starting Comprehensive RAG System Test")
        print("Testing 60 questions across 3 categories")
        print("=" * 70)
        
        # Initialize system
        if not self.initialize_system():
            print("❌ System initialization failed. Cannot proceed with tests.")
            return
        
        # Get test questions
        test_questions = self.get_test_questions()
        
        # Run tests for each category
        all_results = {}
        for category, questions in test_questions.items():
            all_results[category] = self.run_test_category(category, questions)
        
        # Generate summary report
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 70)
        
        summary = self.generate_summary_report(all_results)
        
        # Print category summaries
        for category, stats in summary["categories"].items():
            print(f"\n📁 {category.upper()} Questions:")
            print(f"   Total Questions: {stats['question_count']}")
            print(f"   Average Score: {stats['average_score']:.2f}")
            print(f"   Passed: {stats['passed']}/{stats['question_count']}")
            print(f"   Pass Rate: {stats['pass_rate']:.1f}%")
        
        # Print overall summary
        print(f"\n🎯 OVERALL SYSTEM PERFORMANCE:")
        print(f"   Total Questions Tested: {summary['overall']['total_questions']}")
        print(f"   Overall Score: {summary['overall']['overall_score']:.2f}")
        print(f"   System Status: {summary['overall']['system_status']}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        overall_score = summary['overall']['overall_score']
        if overall_score >= 0.8:
            print("   🎉 Excellent performance! System is production-ready.")
        elif overall_score >= 0.6:
            print("   👍 Good performance with room for improvement in scope detection.")
        elif overall_score >= 0.4:
            print("   ⚠️ Moderate performance. Consider improving embedding quality and LLM responses.")
        else:
            print("   🔧 Significant improvements needed in all areas.")
        
        # Save detailed results
        with open("test_results_detailed.json", "w") as f:
            json.dump({"summary": summary, "detailed_results": all_results}, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: test_results_detailed.json")
        
        return summary

def main():
    """Main function to run the comprehensive test."""
    tester = ComprehensiveRAGTester()
    summary = tester.run_comprehensive_test()
    
    # Return exit code based on performance
    overall_score = summary['overall']['overall_score']
    if overall_score >= 0.7:
        print(f"\n✅ Test completed successfully! System performing well.")
        exit(0)
    elif overall_score >= 0.5:
        print(f"\n⚠️ Test completed with acceptable performance.")
        exit(0)
    else:
        print(f"\n❌ Test completed but system needs improvement.")
        exit(1)

if __name__ == "__main__":
    main()