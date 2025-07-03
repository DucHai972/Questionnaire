#!/usr/bin/env python3
"""
Demo: Real LLM Integration with Format Benchmark
This shows how to extend the benchmark framework to use actual LLM APIs
"""

import json
import time
from benchmark_complete import BenchmarkTasks, DataLoader, BenchmarkResult
from typing import List, Dict, Tuple

class RealLLMEvaluator:
    """
    Example implementation for integrating with real LLM APIs
    Replace with your preferred LLM service (OpenAI, Anthropic, etc.)
    """
    
    def __init__(self, llm_type: str = "mock"):
        self.llm_type = llm_type
        # In real implementation, initialize your LLM client here
        # self.client = openai.OpenAI(api_key="your-key")
        
    def query_llm(self, prompt: str) -> str:
        """
        Query the actual LLM with the prompt
        Replace this with actual LLM API calls
        """
        
        if self.llm_type == "mock":
            # Simulate LLM response with more realistic patterns
            time.sleep(0.1)  # Simulate API latency
            
            # Better mock responses based on prompt content
            if "BOUNDARY DETECTION" in prompt:
                if "R" in prompt:
                    # Extract IDs from prompt
                    import re
                    ids = re.findall(r'"respondent":"([^"]+)"', prompt)
                    if len(ids) >= 3:
                        return f"The three respondent IDs are: {', '.join(ids[:3])}"
                return "I can identify 3 response boundaries in the data"
                
            elif "REVERSE LOOKUP" in prompt:
                # Try to extract the answer value being queried
                match = re.search(r"answer '([^']+)'", prompt)
                if match:
                    answer = match.group(1)
                    return f"The answer '{answer}' belongs to a demographic or profile question"
                return "This answer belongs to one of the survey questions"
                
            elif "ANSWER LOOKUP" in prompt:
                # Try to extract the question being asked
                match = re.search(r"what is the answer to: '([^']+)'", prompt, re.IGNORECASE)
                if match:
                    question = match.group(1)
                    # Extract a potential answer from the data
                    data_match = re.search(r'"' + re.escape(question) + r'":"([^"]+)"', prompt)
                    if data_match:
                        return f"The answer is: {data_match.group(1)}"
                return "Answer found in the provided data"
                
            elif "REASONING TASK" in prompt:
                # Count how many entries might match criteria
                lines = prompt.split('\n')
                data_lines = [l for l in lines if '"respondent"' in l or '"ResponseId"' in l]
                match_count = min(len(data_lines), 3)  # Estimate matches
                return f"Found {match_count} respondents matching the criteria"
                
            elif "COMPLETION TASK" in prompt:
                # Try to predict based on context
                if "Employment" in prompt or "professional" in prompt.lower():
                    return "Based on the profile, I predict: Full-time employed"
                elif "education" in prompt.lower():
                    return "Based on the profile, I predict: Bachelor's degree"
                return "Prediction based on similar profiles"
                
            elif "SEMANTIC RETRIEVAL" in prompt:
                # Extract semantic value from triples
                match = re.search(r'pred:has\w+ "([^"]+)"', prompt)
                if match:
                    return f"The semantic value is: {match.group(1)}"
                return "Semantic attribute extracted from the data"
            
            return "Unable to process this request"
        
        else:
            # Example for OpenAI integration (commented out)
            """
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a data analysis expert. Answer precisely and concisely."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=150,
                    temperature=0.1
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                return f"LLM Error: {str(e)}"
            """
            pass
    
    def score_response(self, expected: str, actual: str, task_type: str) -> float:
        """
        Score the LLM response against expected answer
        This implements more sophisticated scoring than the mock evaluator
        """
        
        if not expected or not actual:
            return 0.0
        
        expected_lower = expected.lower()
        actual_lower = actual.lower()
        
        # Exact match gets full score
        if expected_lower == actual_lower:
            return 1.0
        
        # Task-specific scoring logic
        if task_type == "Task 1":  # Boundary Detection
            # Extract respondent IDs from both expected and actual
            import re
            expected_ids = set(re.findall(r'R?\d+', expected))
            actual_ids = set(re.findall(r'R?\d+', actual))
            
            if expected_ids and actual_ids:
                matches = len(expected_ids & actual_ids)
                return matches / len(expected_ids)
            elif "respondent" in actual_lower or "response" in actual_lower:
                return 0.5  # Partial credit for understanding task
            
        elif task_type == "Task 2":  # Reverse Lookup
            # Check if key terms from expected answer appear in response
            expected_words = set(expected_lower.split())
            actual_words = set(actual_lower.split())
            key_words = {"question", "answer", "demographic", "profile", "survey"}
            
            if expected_words & actual_words:
                return 0.8  # High score for containing expected terms
            elif key_words & actual_words:
                return 0.6  # Medium score for understanding domain
                
        elif task_type == "Task 3":  # Answer Lookup
            # Look for the expected answer in the response
            expected_value = expected.replace("Answer: ", "").strip()
            if expected_value.lower() in actual_lower:
                return 1.0
            elif "answer" in actual_lower:
                return 0.4  # Partial credit for attempting answer
                
        elif task_type == "Task 4":  # Knowledge Chain Reasoning
            # Check if respondent counts or IDs are mentioned
            expected_nums = set(re.findall(r'\d+', expected))
            actual_nums = set(re.findall(r'\d+', actual))
            
            if expected_nums & actual_nums:
                return 0.8  # Good score for finding correct numbers
            elif "matching" in actual_lower or "found" in actual_lower:
                return 0.5  # Partial credit for understanding task
                
        elif task_type == "Task 5":  # Answer Completion
            # Check if prediction makes sense in context
            expected_value = expected.replace("Predicted: ", "").strip()
            if expected_value.lower() in actual_lower:
                return 1.0
            elif "predict" in actual_lower or "based on" in actual_lower:
                return 0.6  # Credit for making a prediction attempt
                
        elif task_type == "Task 6":  # Semantic Retrieval
            # Check if semantic value is extracted
            expected_value = expected.replace("Value: ", "").strip()
            if expected_value.lower() in actual_lower:
                return 1.0
            elif "semantic" in actual_lower or "value" in actual_lower:
                return 0.5  # Credit for understanding semantic task
        
        # Fallback: general similarity scoring
        common_words = set(expected_lower.split()) & set(actual_lower.split())
        if common_words:
            return len(common_words) / len(set(expected_lower.split()))
        
        return 0.1  # Minimal score for any response

class RealLLMBenchmark:
    """
    Enhanced benchmark that uses real LLM evaluation
    """
    
    def __init__(self, dataset: str = "stack_overflow", llm_type: str = "mock"):
        self.dataset = dataset
        self.data_loader = DataLoader()
        self.benchmark_tasks = BenchmarkTasks(self.data_loader)
        self.evaluator = RealLLMEvaluator(llm_type)
        self.results = []
    
    def run_single_task_demo(self, task_name: str = "Task 1", num_iterations: int = 3):
        """
        Run a demo of a single task to show real LLM integration
        """
        
        print(f"🚀 Real LLM Demo: {task_name} on {self.dataset.upper()}")
        print("=" * 60)
        
        # Get task function
        task_functions = {
            "Task 1": self.benchmark_tasks.task_1_boundary_detection,
            "Task 2": self.benchmark_tasks.task_2_answer_reverse_lookup,
            "Task 3": self.benchmark_tasks.task_3_answer_lookup,
            "Task 4": self.benchmark_tasks.task_4_knowledge_chain_reasoning,
            "Task 5": self.benchmark_tasks.task_5_answer_completion,
            "Task 6": self.benchmark_tasks.task_6_semantic_attribute_retrieval
        }
        
        task_function = task_functions.get(task_name)
        if not task_function:
            print(f"❌ Task {task_name} not found")
            return
        
        formats = ["json", "html", "xml", "markdown", "txt"]
        
        for format_type in formats:
            print(f"\n📋 Testing {format_type.upper()} format:")
            format_scores = []
            
            for i in range(num_iterations):
                try:
                    start_time = time.time()
                    
                    # Generate task prompt and expected answer
                    prompt, expected = task_function(self.dataset, format_type)
                    
                    print(f"\n  🔍 Iteration {i+1}:")
                    print(f"     Expected: {expected}")
                    
                    # Query real LLM
                    llm_response = self.evaluator.query_llm(prompt)
                    print(f"     LLM Said: {llm_response}")
                    
                    # Score the response
                    score = self.evaluator.score_response(expected, llm_response, task_name)
                    print(f"     Score: {score:.3f}")
                    
                    execution_time = time.time() - start_time
                    
                    # Record result
                    result = BenchmarkResult(
                        task=task_name,
                        format=format_type,
                        score=score,
                        expected_answer=expected,
                        llm_response=llm_response,
                        prompt=prompt[:300] + "..." if len(prompt) > 300 else prompt
                    )
                    
                    self.results.append(result)
                    format_scores.append(score)
                    
                except Exception as e:
                    print(f"     ❌ Error: {str(e)}")
                    format_scores.append(0.0)
            
            avg_score = sum(format_scores) / len(format_scores)
            performance = "🟢 Excellent" if avg_score > 0.8 else "🟡 Good" if avg_score > 0.6 else "🔴 Poor"
            print(f"\n  📊 {format_type.upper()} Average: {avg_score:.3f} {performance}")
        
        print(f"\n{'='*60}")
        print(f"✅ Demo completed! Tested {len(self.results)} scenarios")
    
    def compare_formats_on_task(self, task_name: str = "Task 1"):
        """
        Quick comparison of all formats on a single task
        """
        
        print(f"🔬 Format Comparison: {task_name}")
        print("-" * 40)
        
        task_functions = {
            "Task 1": self.benchmark_tasks.task_1_boundary_detection,
            "Task 2": self.benchmark_tasks.task_2_answer_reverse_lookup,
            "Task 3": self.benchmark_tasks.task_3_answer_lookup,
            "Task 4": self.benchmark_tasks.task_4_knowledge_chain_reasoning,
            "Task 5": self.benchmark_tasks.task_5_answer_completion,
            "Task 6": self.benchmark_tasks.task_6_semantic_attribute_retrieval
        }
        
        task_function = task_functions.get(task_name)
        formats = ["json", "xml", "html", "markdown", "txt"]
        results = {}
        
        for format_type in formats:
            try:
                prompt, expected = task_function(self.dataset, format_type)
                llm_response = self.evaluator.query_llm(prompt)
                score = self.evaluator.score_response(expected, llm_response, task_name)
                results[format_type] = {
                    "score": score,
                    "response": llm_response[:100] + "..." if len(llm_response) > 100 else llm_response
                }
            except Exception as e:
                results[format_type] = {"score": 0.0, "response": f"Error: {str(e)}"}
        
        # Sort by score
        sorted_results = sorted(results.items(), key=lambda x: x[1]["score"], reverse=True)
        
        print("Ranking | Format | Score | Response Preview")
        print("-" * 80)
        for i, (format_type, data) in enumerate(sorted_results):
            rank_icon = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "📍"
            print(f"{rank_icon} {i+1:>4} | {format_type.upper():>8} | {data['score']:.3f} | {data['response']}")
        
        return sorted_results

def main():
    """
    Demo showcasing real LLM integration capabilities
    """
    
    print("🧠 Real LLM Benchmark Integration Demo")
    print("=" * 80)
    print()
    print("This demo shows how to extend the benchmark framework with actual LLM APIs")
    print("Currently using enhanced mock responses - replace with your LLM service")
    print()
    
    # Demo 1: Single task across all formats
    print("📊 DEMO 1: Task 1 (Boundary Detection) across all formats")
    benchmark = RealLLMBenchmark("stack_overflow", "mock")
    benchmark.run_single_task_demo("Task 1", num_iterations=2)
    
    print("\n" + "="*80)
    
    # Demo 2: Quick format comparison
    print("🔬 DEMO 2: Quick format comparison on Task 3 (Answer Lookup)")
    benchmark2 = RealLLMBenchmark("sus_uta7", "mock") 
    results = benchmark2.compare_formats_on_task("Task 3")
    
    print(f"\n🏆 Winner: {results[0][0].upper()} format with {results[0][1]['score']:.3f} score")
    
    print("\n" + "="*80)
    print("🚀 Integration Instructions:")
    print()
    print("To use with real LLMs:")
    print("1. Replace RealLLMEvaluator.query_llm() with actual API calls")
    print("2. Add your API credentials and configuration")
    print("3. Adjust scoring logic based on your LLM's response patterns")
    print("4. Consider rate limiting and error handling for production use")
    print()
    print("Supported LLM Services:")
    print("- OpenAI GPT (GPT-4, GPT-3.5)")
    print("- Anthropic Claude")
    print("- Google Gemini")
    print("- Local models via Ollama/LocalAI")
    print("- Any REST API-based LLM service")

if __name__ == "__main__":
    main() 