import json
import random
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
import xml.etree.ElementTree as ET

@dataclass
class BenchmarkResult:
    task: str
    format: str
    score: float
    expected_answer: str
    llm_response: str
    prompt: str
    execution_time: float = 0.0

@dataclass
class TaskResult:
    task_name: str
    format_scores: Dict[str, float]
    average_score: float

class DataLoader:
    """Load and parse data from different formats"""
    
    def __init__(self, base_dir: str = "preprocessed_data"):
        self.base_dir = base_dir
        self.datasets = {
            "mental_health": "self-repoted-mental-health-college-students-2022",
            "stack_overflow": "stack-overflow-2022-developer-survey", 
            "sus_uta7": "sus-uta7"
        }
    
    def load_json_data(self, dataset: str) -> Dict:
        """Load JSON data"""
        if dataset == "mental_health":
            path = os.path.join(self.base_dir, self.datasets[dataset], "mental_health_questionnaire.json")
        elif dataset == "stack_overflow":
            path = os.path.join(self.base_dir, self.datasets[dataset], "survey_results_sample.json")
        elif dataset == "sus_uta7":
            path = os.path.join(self.base_dir, self.datasets[dataset], "sus_uta7_questionnaire.json")
        
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_html_data(self, dataset: str) -> str:
        """Load HTML data"""
        if dataset == "mental_health":
            path = os.path.join(self.base_dir, self.datasets[dataset], "mental_health_questionnaire.html")
        elif dataset == "stack_overflow":
            path = os.path.join(self.base_dir, self.datasets[dataset], "survey_results_sample.html")
        elif dataset == "sus_uta7":
            path = os.path.join(self.base_dir, self.datasets[dataset], "sus_uta7_questionnaire.html")
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_xml_data(self, dataset: str) -> str:
        """Load XML data"""
        if dataset == "mental_health":
            path = os.path.join(self.base_dir, self.datasets[dataset], "mental_health_questionnaire.xml")
        elif dataset == "stack_overflow":
            path = os.path.join(self.base_dir, self.datasets[dataset], "survey_results_sample.xml")
        elif dataset == "sus_uta7":
            path = os.path.join(self.base_dir, self.datasets[dataset], "sus_uta7_questionnaire.xml")
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_markdown_data(self, dataset: str) -> str:
        """Load Markdown data"""
        if dataset == "mental_health":
            path = os.path.join(self.base_dir, self.datasets[dataset], "mental_health_questionnaire.md")
        elif dataset == "stack_overflow":
            path = os.path.join(self.base_dir, self.datasets[dataset], "survey_results_sample.md")
        elif dataset == "sus_uta7":
            path = os.path.join(self.base_dir, self.datasets[dataset], "sus_uta7_questionnaire.md")
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def load_txt_data(self, dataset: str) -> str:
        """Load TXT data"""
        if dataset == "mental_health":
            path = os.path.join(self.base_dir, self.datasets[dataset], "mental_health_questionnaire.txt")
        elif dataset == "stack_overflow":
            path = os.path.join(self.base_dir, self.datasets[dataset], "survey_results_sample.txt")
        elif dataset == "sus_uta7":
            path = os.path.join(self.base_dir, self.datasets[dataset], "sus_uta7_questionnaire.txt")
        
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

class BenchmarkTasks:
    """Implementation of the 6 benchmark tasks"""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
        self.formats = ["json", "html", "xml", "markdown", "txt"]
    
    def task_1_boundary_detection(self, dataset: str, format_type: str) -> Tuple[str, str]:
        """Task 1: Question Block Boundary Detection"""
        
        if format_type == "json":
            data = self.data_loader.load_json_data(dataset)
            
            if dataset == "stack_overflow":
                responses = data.get('responses', [])
                # Select 3 consecutive respondents
                start_idx = random.randint(0, len(responses) - 3)
                selected = responses[start_idx:start_idx + 3]
                
                concatenated = ""
                respondent_ids = []
                for resp in selected:
                    resp_id = resp['answers'].get('ResponseId', f"R{random.randint(1000, 9999)}")
                    respondent_ids.append(str(resp_id))
                    concatenated += json.dumps({"respondent": resp_id, "answers": resp['answers']}, separators=(',', ':'))
                
                expected = f"Respondents: {', '.join(respondent_ids)}"
                
                prompt = f"""BOUNDARY DETECTION TASK:

The following data contains responses from exactly 3 different respondents concatenated together. Identify the respondent IDs in order.

Data:
{concatenated}

Please list the 3 respondent IDs you found:"""
                
                return prompt, expected
            
            else:
                responses = data.get('responses', []) or data.get('datasets', {}).get('responses', [])
                start_idx = random.randint(0, len(responses) - 3)
                selected = responses[start_idx:start_idx + 3]
                
                concatenated = ""
                respondent_ids = []
                for i, resp in enumerate(selected):
                    resp_id = f"R{start_idx + i + 1}"
                    respondent_ids.append(resp_id)
                    concatenated += json.dumps({"respondent": resp_id, "answers": resp.get('answers', resp)}, separators=(',', ':'))
                
                expected = f"Respondents: {', '.join(respondent_ids)}"
                
                prompt = f"""BOUNDARY DETECTION TASK:

The following data contains responses from exactly 3 different respondents concatenated together. Identify the respondent IDs in order.

Data:
{concatenated}

Please list the 3 respondent IDs you found:"""
                
                return prompt, expected
        
        else:
            expected = "Format does not support boundary detection"
            prompt = "Non-JSON formats not fully implemented for boundary detection"
            return prompt, expected
    
    def task_2_answer_reverse_lookup(self, dataset: str, format_type: str) -> Tuple[str, str]:
        """Task 2: Answer Reverse Lookup"""
        
        if format_type == "json":
            data = self.data_loader.load_json_data(dataset)
            
            if dataset == "stack_overflow":
                responses = data.get('responses', [])
                questions = data.get('questions', [])
                
                # Select random respondent
                respondent = random.choice(responses)
                answers = respondent['answers']
                
                # Pick random answer
                answer_key, answer_value = random.choice(list(answers.items()))
                
                # Find corresponding question
                question_desc = None
                for q in questions:
                    if q.startswith(f"{answer_key}:"):
                        question_desc = q.split(":", 1)[1].strip()
                        break
                
                if not question_desc:
                    question_desc = answer_key
                
                expected = f"Question: {question_desc}"
                
                prompt = f"""ANSWER REVERSE LOOKUP TASK:

Given this respondent's complete data:
{json.dumps(respondent, indent=2)}

Available questions:
{json.dumps(questions[:10], indent=2)}

Which question does the answer '{answer_value}' belong to for this respondent?"""
                
            else:
                # Handle other datasets
                responses = data.get('responses', []) or data.get('datasets', {}).get('responses', [])
                questions = data.get('questions', {}) or data.get('datasets', {}).get('questions', {})
                
                respondent = random.choice(responses)
                answers = respondent.get('answers', respondent)
                
                # Pick random answer
                answer_key, answer_value = random.choice(list(answers.items()))
                
                # Get question description
                question_desc = questions.get(answer_key, answer_key)
                expected = f"Question: {question_desc}"
                
                prompt = f"""ANSWER REVERSE LOOKUP TASK:

Given this respondent's complete data:
{json.dumps(respondent, indent=2)}

Question metadata available:
{json.dumps(questions, indent=2)}

Which question does the answer '{answer_value}' belong to for this respondent?"""
            
            return prompt, expected
        
        else:
            expected = "Non-JSON reverse lookup not implemented"
            prompt = "Format does not support detailed reverse lookup"
            return prompt, expected
    
    def task_3_answer_lookup(self, dataset: str, format_type: str) -> Tuple[str, str]:
        """Task 3: Answer Lookup"""
        
        if format_type == "json":
            data = self.data_loader.load_json_data(dataset)
            responses = data.get('responses', []) or data.get('datasets', {}).get('responses', [])
            
            # Select random respondent and question
            respondent = random.choice(responses)
            answers = respondent.get('answers', respondent)
            
            question_key, answer_value = random.choice(list(answers.items()))
            
            respondent_id = respondent.get('respondent', 'R123')
            expected = f"Answer: {answer_value}"
            
            prompt = f"""ANSWER LOOKUP TASK:

For respondent {respondent_id}, what is the answer to: '{question_key}'?

Respondent data:
{json.dumps(respondent, indent=2)}"""
            
            return prompt, expected
        
        else:
            expected = "Non-JSON answer lookup not implemented"
            prompt = "Format does not support detailed answer lookup"
            return prompt, expected
    
    def task_4_knowledge_chain_reasoning(self, dataset: str, format_type: str) -> Tuple[str, str]:
        """Task 4: Knowledge Chain Reasoning"""
        
        if format_type == "json":
            data = self.data_loader.load_json_data(dataset)
            responses = data.get('responses', []) or data.get('datasets', {}).get('responses', [])
            
            # Select 10 respondents for reasoning context
            selected_respondents = random.sample(responses, min(10, len(responses)))
            
            if dataset == "stack_overflow":
                # Find respondents who are employed full-time AND in specific employment category
                criteria_1 = "Employed, full-time"
                criteria_2 = "I am a developer by profession"
                
                matching_ids = []
                for resp in selected_respondents:
                    answers = resp['answers']
                    employment = answers.get('Employment', '')
                    main_branch = answers.get('MainBranch', '')
                    resp_id = answers.get('ResponseId', 'Unknown')
                    
                    if criteria_1 in employment and criteria_2 in main_branch:
                        matching_ids.append(str(resp_id))
                
                expected = f"Matching respondents: {', '.join(matching_ids)}" if matching_ids else "No matching respondents found"
                
                prompt = f"""MULTI-HOP REASONING TASK:

Find all respondents who are both 'Employed, full-time' AND identify as 'I am a developer by profession'

Survey Data:
"""
                for resp in selected_respondents:
                    prompt += json.dumps(resp, separators=(',', ':')) + "\n"
                
                prompt += "\nPlease identify all respondent IDs that match BOTH criteria:"
                
            else:
                # For other datasets, use generic multi-criteria search
                # Example: Find all senior employees in specific department
                matching_ids = []
                for i, resp in enumerate(selected_respondents):
                    answers = resp.get('answers', resp)
                    resp_id = f"R{i+1}"
                    
                    # Check for any two criteria that might exist
                    has_criteria_1 = any(str(v).lower() in ['senior', 'high', 'advanced'] for v in answers.values())
                    has_criteria_2 = any(str(v).lower() in ['male', 'female', 'it', 'technical'] for v in answers.values())
                    
                    if has_criteria_1 and has_criteria_2:
                        matching_ids.append(resp_id)
                
                expected = f"Matching respondents: {', '.join(matching_ids)}" if matching_ids else "No matching respondents found"
                
                prompt = f"""MULTI-HOP REASONING TASK:

Find all respondents who have both senior-level indicators AND specific demographic/department markers

Survey Data:
"""
                for i, resp in enumerate(selected_respondents):
                    resp_data = {"respondent": f"R{i+1}", "answers": resp.get('answers', resp)}
                    prompt += json.dumps(resp_data, separators=(',', ':')) + "\n"
                
                prompt += "\nPlease identify all respondent IDs that match BOTH criteria:"
            
            return prompt, expected
        
        else:
            expected = "Non-JSON reasoning not implemented"
            prompt = "Format does not support complex reasoning tasks"
            return prompt, expected
    
    def task_5_answer_completion(self, dataset: str, format_type: str) -> Tuple[str, str]:
        """Task 5: Answer Completion"""
        
        if format_type == "json":
            data = self.data_loader.load_json_data(dataset)
            responses = data.get('responses', []) or data.get('datasets', {}).get('responses', [])
            
            # Select random respondent
            respondent = random.choice(responses)
            answers = respondent.get('answers', respondent)
            
            # Pick random field to predict
            answer_keys = list(answers.keys())
            target_key = random.choice(answer_keys)
            target_value = answers[target_key]
            
            # Create partial data (remove target field)
            partial_answers = {k: v for k, v in answers.items() if k != target_key}
            
            expected = f"Predicted answer: {target_value}"
            
            prompt = f"""ANSWER COMPLETION TASK:

Given respondent's other answers:
{json.dumps(partial_answers, indent=2)}

Predict the answer to '{target_key}'

Provide your prediction with reasoning:"""
            
            return prompt, expected
        
        else:
            expected = "Non-JSON completion not implemented"
            prompt = "Format does not support answer completion"
            return prompt, expected
    
    def task_6_semantic_attribute_retrieval(self, dataset: str, format_type: str) -> Tuple[str, str]:
        """Task 6: Semantic Attribute Retrieval"""
        
        if format_type == "json":
            data = self.data_loader.load_json_data(dataset)
            responses = data.get('responses', []) or data.get('datasets', {}).get('responses', [])
            
            # Select random respondent
            respondent = random.choice(responses)
            answers = respondent.get('answers', respondent)
            
            # Create semantic queries for available attributes
            semantic_mappings = {
                'gender': ['gender', 'sex', 'male', 'female'],
                'age': ['age', 'birth', 'year'],
                'education': ['education', 'degree', 'school'],
                'employment': ['employment', 'job', 'work', 'profession'],
                'department': ['department', 'team', 'division']
            }
            
            # Find applicable semantic attribute
            found_attribute = None
            found_value = None
            semantic_query = None
            
            for semantic_attr, keywords in semantic_mappings.items():
                for key, value in answers.items():
                    if any(keyword in key.lower() for keyword in keywords):
                        found_attribute = semantic_attr
                        found_value = value
                        semantic_query = f"'{semantic_attr} identity'"
                        break
                if found_attribute:
                    break
            
            if not found_attribute:
                # Fallback to first available attribute
                first_key, first_value = next(iter(answers.items()))
                found_attribute = first_key
                found_value = first_value
                semantic_query = f"'{first_key}'"
            
            resp_id = f"emp:R{random.randint(1000, 9999)}"
            
            # Create RDF-like triples for knowledge graph format
            triples = []
            for key, value in answers.items():
                predicate = f"pred:has{key.replace(' ', '').replace('?', '')}"
                triples.append(f'{resp_id} {predicate} "{value}" .')
            
            expected = f"Value: {found_value}"
            
            prompt = f"""SEMANTIC ATTRIBUTE RETRIEVAL TASK:

Given these triples for {resp_id}:
{chr(10).join(triples)}

Extract the semantic attribute {semantic_query} for {resp_id}"""
            
            return prompt, expected
        
        else:
            expected = "Non-JSON semantic retrieval not implemented"
            prompt = "Format does not support semantic attribute retrieval"
            return prompt, expected

class MockLLMEvaluator:
    """Mock LLM responses for testing the benchmark"""
    
    def evaluate_response(self, task_type: str, expected: str, format_type: str) -> Tuple[str, float]:
        """Generate mock response and score"""
        
        # Simulate format-dependent accuracy
        format_accuracy = {
            "json": 0.9,
            "html": 0.7,
            "xml": 0.8,
            "markdown": 0.6,
            "txt": 0.5
        }
        
        base_accuracy = format_accuracy.get(format_type, 0.5)
        # Add some randomness
        actual_score = base_accuracy + random.uniform(-0.2, 0.2)
        actual_score = max(0.0, min(1.0, actual_score))
        
        # Generate response based on expected
        response = f"Mock response for {task_type}: {expected}"
        
        return response, actual_score

class LLMFormatBenchmark:
    """Main benchmark orchestrator"""
    
    def __init__(self, dataset: str = "stack_overflow"):
        self.dataset = dataset
        self.data_loader = DataLoader()
        self.benchmark_tasks = BenchmarkTasks(self.data_loader)
        self.evaluator = MockLLMEvaluator()
        self.results = []
    
    def run_benchmark(self, num_iterations: int = 3) -> List[TaskResult]:
        """Run complete benchmark across all tasks and formats"""
        
        tasks = [
            ("Task 1", self.benchmark_tasks.task_1_boundary_detection),
        ]
        
        formats = ["json", "html", "xml", "markdown", "txt"]
        
        print(f"🚀 Running LLM Format Benchmark on {self.dataset} dataset")
        print(f"📊 Testing {len(tasks)} tasks across {len(formats)} formats with {num_iterations} iterations each")
        print("=" * 80)
        
        task_results = []
        
        for task_name, task_function in tasks:
            print(f"\n📋 {task_name}: {task_function.__doc__.split(':', 1)[0] if task_function.__doc__ else ''}")
            
            format_scores = {}
            
            for format_type in formats:
                total_score = 0.0
                
                for iteration in range(num_iterations):
                    try:
                        # Generate task
                        prompt, expected = task_function(self.dataset, format_type)
                        
                        # Get mock LLM response and score
                        llm_response, score = self.evaluator.evaluate_response(task_name, expected, format_type)
                        
                        # Record result
                        result = BenchmarkResult(
                            task=task_name,
                            format=format_type,
                            score=score,
                            expected_answer=expected,
                            llm_response=llm_response,
                            prompt=prompt[:200] + "..." if len(prompt) > 200 else prompt
                        )
                        
                        self.results.append(result)
                        total_score += score
                        
                    except Exception as e:
                        print(f"   ❌ Error in {format_type}: {str(e)}")
                        total_score += 0.0
                
                avg_score = total_score / num_iterations
                format_scores[format_type] = avg_score
                print(f"   {format_type.upper():>10}: {avg_score:.3f}")
            
            # Calculate task average
            task_avg = sum(format_scores.values()) / len(format_scores)
            task_result = TaskResult(task_name, format_scores, task_avg)
            task_results.append(task_result)
            
            print(f"   {'AVERAGE':>10}: {task_avg:.3f}")
        
        return task_results

def main():
    """Run a simple benchmark test"""
    
    print("🧪 Testing LLM Format Benchmark Framework")
    
    try:
        # Test with stack overflow dataset
        benchmark = LLMFormatBenchmark("stack_overflow")
        task_results = benchmark.run_benchmark(num_iterations=2)
        
        print(f"\n✅ Benchmark completed successfully!")
        print(f"📊 Tested {len(task_results)} tasks")
        print(f"💾 Generated {len(benchmark.results)} test cases")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {str(e)}")

if __name__ == "__main__":
    main() 