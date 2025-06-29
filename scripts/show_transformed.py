import json
import os

def show_transformed_structure():
    # Read the transformed JSON
    file_path = os.path.join('preprocessed_data', 'self-repoted-mental-health-college-students-2022', 'transformed_data.json')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("TRANSFORMED QUESTION METADATA:")
    print("=" * 50)
    
    # Show single questions
    print("\nSingle questions (converted format):")
    single_count = 0
    for key, value in data['question_metadata'].items():
        if 'base_question' in value and 'sub_questions' not in value:
            if single_count < 3:  # Show first 3
                print(f'"{key}": {{')
                print(f'  "base_question": "{value["base_question"]}"')
                print('}')
                print()
            single_count += 1
    
    # Show grouped questions
    print("\nGrouped questions (updated keys):")
    grouped_count = 0
    for key, value in data['question_metadata'].items():
        if 'sub_questions' in value:
            if grouped_count < 2:  # Show first 2
                print(f'"{key}": {{')
                print(f'  "base_question": "{value["base_question"]}"')
                print(f'  "sub_questions": {{')
                for sub_key, sub_value in value["sub_questions"].items():
                    print(f'    "{sub_key}": "{sub_value}"')
                print('  }')
                print('}')
                print()
            grouped_count += 1
    
    # Show sample response structure
    print("\nSAMPLE RESPONSE STRUCTURE:")
    print("=" * 50)
    sample_response = data['responses'][0]['answers']
    
    print("Single question answers:")
    count = 0
    for key, value in sample_response.items():
        if not isinstance(value, dict) and count < 3:
            print(f'"{key}": {json.dumps(value)}')
            count += 1
    
    print("\nGrouped question answers:")
    count = 0
    for key, value in sample_response.items():
        if isinstance(value, dict) and count < 2:
            print(f'"{key}": {json.dumps(value, indent=2)}')
            count += 1

if __name__ == "__main__":
    show_transformed_structure() 