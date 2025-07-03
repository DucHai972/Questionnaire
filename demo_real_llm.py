#!/usr/bin/env python3
"""
Demo: Real LLM Integration with Format Benchmark
Shows how to extend the benchmark framework to use actual LLM APIs
"""

import json
import time
import re
from benchmark_complete import BenchmarkTasks, DataLoader, BenchmarkResult

class RealLLMEvaluator:
    """Example implementation for integrating with real LLM APIs"""
    
    def __init__(self, llm_type: str = "mock"):
        self.llm_type = llm_type
        # In real implementation, initialize your LLM client here
    
    def query_llm(self, prompt: str) -> str:
        """Query the actual LLM - replace with real API calls"""
        
        # Simulate API latency
        time.sleep(0.1)
        
        # Enhanced mock responses based on prompt analysis
        if "BOUNDARY DETECTION" in prompt:
            ids = re.findall(r'"respondent":"([^"]+)"', prompt)
            if len(ids) >= 3:
                return f"The three respondent IDs are: {', '.join(ids[:3])}"
            return "I can identify 3 response boundaries in the data"
            
        elif "REVERSE LOOKUP" in prompt:
            match = re.search(r"answer '([^']+)'", prompt)
            if match:
                answer = match.group(1)
                return f"The answer '{answer}' belongs to a demographic question"
            return "This answer belongs to one of the survey questions"
            
        elif "ANSWER LOOKUP" in prompt:
            match = re.search(r"what is the answer to: '([^']+)'", prompt, re.IGNORECASE)
            if match:
                question = match.group(1)
                data_match = re.search(r'"' + re.escape(question) + r'":"([^"]+)"', prompt)
                if data_match:
                    return f"The answer is: {data_match.group(1)}"
            return "Answer found in the provided data"
            
        elif "REASONING TASK" in prompt:
            lines = [l for l in prompt.split('\n') if '"respondent"' in l]
            match_count = min(len(lines), 3)
            return f"Found {match_count} respondents matching the criteria"
            
        elif "COMPLETION TASK" in prompt:
            if "Employment" in prompt:
                return "Based on the profile, I predict: Full-time employed"
            return "Prediction based on similar profiles"
            
        elif "SEMANTIC RETRIEVAL" in prompt:
            match = re.search(r'pred:has\w+ "([^"]+)"', prompt)
            if match:
                return f"The semantic value is: {match.group(1)}"
            return "Semantic attribute extracted"
        
        return "Unable to process this request"
    
    def score_response(self, expected: str, actual: str, task_type: str) -> float:
        """Score LLM response against expected answer"""
        
        if not expected or not actual:
            return 0.0
        
        expected_lower = expected.lower()
        actual_lower = actual.lower()
        
        # Exact match
        if expected_lower == actual_lower:
            return 1.0
        
        # Task-specific scoring
        if task_type == "Task 1":  # Boundary Detection
            expected_ids = set(re.findall(r'R?\d+', expected))
            actual_ids = set(re.findall(r'R?\d+', actual))
            
            if expected_ids and actual_ids:
                matches = len(expected_ids & actual_ids)
                return matches / len(expected_ids)
            elif "respondent" in actual_lower:
                return 0.5
        
        # General similarity
        expected_words = set(expected_lower.split())
        actual_words = set(actual_lower.split())
        common_words = expected_words & actual_words
        
        if expected_words:
            return len(common_words) / len(expected_words)
        
        return 0.1

class RealLLMBenchmark:
    """Enhanced benchmark using real LLM evaluation"""
    
    def __init__(self, dataset: str = "stack_overflow"):
        self.dataset = dataset
        self.data_loader = DataLoader()
        self.benchmark_tasks = BenchmarkTasks(self.data_loader)
        self.evaluator = RealLLMEvaluator()
        self.results = []
    
    def quick_demo(self, task_name: str = "Task 1"):
        """Quick demo of format comparison"""
        
        print(f"🔬 Format Comparison: {task_name}")
        print("-" * 50)
        
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
                    "response": llm_response[:60] + "..." if len(llm_response) > 60 else llm_response
                }
                print(f"{format_type.upper():>10}: {score:.3f} - {results[format_type]['response']}")
            except Exception as e:
                results[format_type] = {"score": 0.0, "response": f"Error: {str(e)}"}
                print(f"{format_type.upper():>10}: 0.000 - Error")
        
        # Show winner
        best_format = max(results.items(), key=lambda x: x[1]["score"])
        print(f"\n🏆 Best: {best_format[0].upper()} ({best_format[1]['score']:.3f})")
        
        return results

def main():
    """Demo showcasing real LLM integration"""
    
    print("🧠 Real LLM Benchmark Integration Demo")
    print("=" * 60)
    print()
    
    # Test different tasks
    benchmark = RealLLMBenchmark("stack_overflow")
    
    print("🧪 Testing Task 1: Boundary Detection")
    benchmark.quick_demo("Task 1")
    
    print("\n🧪 Testing Task 3: Answer Lookup")
    benchmark.quick_demo("Task 3")
    
    print("\n" + "="*60)
    print("🚀 Integration Guide:")
    print("1. Replace query_llm() with real API calls")
    print("2. Add API credentials and configuration")
    print("3. Adjust scoring for your LLM's patterns")
    print("4. Add rate limiting for production use")
    print()
    print("Compatible with: OpenAI, Anthropic, Google, Local models")

if __name__ == "__main__":
    main() 