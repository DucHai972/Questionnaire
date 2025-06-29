import json
import os
import re

def create_concise_label(question_key, question_content):
    """Create a concise, informative label from question key and content"""
    
    # Extract question number from key (e.g., "Q5" from "Q5. How many")
    q_num_match = re.match(r'(Q\d+)\.', question_key)
    if not q_num_match:
        return question_key
    
    q_num = q_num_match.group(1)
    
    # Define mappings for common question patterns
    label_mappings = {
        # Demographics
        'year of birth': 'Birth year',
        'gender': 'Gender',
        'socio-economic status': 'Socioeconomic status',
        'culture': 'Cultural identity',
        'parents receive': 'Parents education',
        
        # Life satisfaction and wellbeing
        'satisfied.*life': 'Life satisfaction',
        'happy.*feel': 'Happiness level',
        'laugh': 'Laughter frequency',
        'learn.*exciting': 'Learning experiences',
        'enjoy.*activities': 'Activity enjoyment',
        'worried.*feel': 'Worry level',
        'depressed.*feel': 'Depression level',
        'angry.*feel': 'Anger level',
        'stress.*feel': 'Stress level',
        'lonely.*unsupported': 'Loneliness level',
        
        # Emotional and mental health scales
        'emotional.*state': 'Emotional state scale',
        'control.*important': 'Life control scale',
        'anxious': 'Anxiety scale',
        'depression': 'Depression scale',
        
        # Specific question patterns
        'unexpectedly': 'Unexpected events',
        'confident': 'Confidence level',
        'problems': 'Problem handling',
        'nervous': 'Nervousness',
        'restless': 'Restlessness',
        'hopeless': 'Hopelessness',
        'worthless': 'Self-worth',
        'concentration': 'Concentration',
        'sleep': 'Sleep patterns',
        'appetite': 'Appetite changes',
        'energy': 'Energy level',
        'moving.*speaking': 'Motor activity',
    }
    
    # Get the base question text to analyze
    if isinstance(question_content, dict):
        base_text = question_content.get('base_question', '').lower()
    else:
        base_text = str(question_content).lower()
    
    # Try to match patterns and create concise labels
    for pattern, label in label_mappings.items():
        if re.search(pattern, base_text):
            return f"{q_num}. {label}"
    
    # Fallback: extract key concepts from the question
    # Remove common question starters and stopwords
    clean_text = re.sub(r'^(how|what|in|next|did|please|according to)', '', base_text)
    clean_text = re.sub(r'\b(is|are|was|were|your|you|the|a|an|to|of|in|on|at|for|with|by)\b', '', clean_text)
    
    # Extract meaningful words (more than 3 characters, not numbers)
    words = [word.strip() for word in clean_text.split() if len(word.strip()) > 3 and not word.strip().isdigit()]
    
    # Take first 2-3 meaningful words and capitalize
    if words:
        if len(words) >= 2:
            label = ' '.join(words[:2]).title()
        else:
            label = words[0].title()
        return f"{q_num}. {label}"
    
    # Ultimate fallback: use original key
    return question_key

def transform_question_metadata(question_metadata):
    """Transform question metadata with concise labels"""
    transformed = {}
    
    for old_key, content in question_metadata.items():
        # Create new concise label
        new_key = create_concise_label(old_key, content)
        
        if isinstance(content, dict):
            # Grouped question - keep structure but update key
            transformed[new_key] = content
        else:
            # Single question - convert to nested structure
            transformed[new_key] = {
                "base_question": content
            }
    
    return transformed

def update_responses(responses, old_to_new_mapping):
    """Update response keys to match new question labels"""
    updated_responses = []
    
    for response in responses:
        updated_answers = {}
        
        for old_key, answer in response['answers'].items():
            # Find corresponding new key
            new_key = old_to_new_mapping.get(old_key, old_key)
            updated_answers[new_key] = answer
        
        updated_responses.append({
            "respondent": response['respondent'],
            "answers": updated_answers
        })
    
    return updated_responses

def transform_questionnaire():
    """Main function to transform the questionnaire JSON"""
    
    # Read the current JSON
    input_path = os.path.join('preprocessed_data', 'self-repoted-mental-health-college-students-2022', 'raw_data.json')
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("Reading current questionnaire data...")
        print(f"Found {len(data['question_metadata'])} questions")
        print(f"Found {len(data['responses'])} responses")
        
        # Show current question keys
        print("\nCurrent question keys (first 10):")
        for i, key in enumerate(list(data['question_metadata'].keys())[:10]):
            print(f"  {i+1}. {key}")
        
        # Transform question metadata
        print("\nTransforming question labels...")
        new_question_metadata = transform_question_metadata(data['question_metadata'])
        
        # Create mapping from old keys to new keys
        old_keys = list(data['question_metadata'].keys())
        new_keys = list(new_question_metadata.keys())
        old_to_new_mapping = dict(zip(old_keys, new_keys))
        
        # Show new question keys
        print("\nNew question keys (first 10):")
        for i, key in enumerate(list(new_question_metadata.keys())[:10]):
            print(f"  {i+1}. {key}")
        
        # Update responses with new keys
        print("\nUpdating response data...")
        updated_responses = update_responses(data['responses'], old_to_new_mapping)
        
        # Create new data structure
        transformed_data = {
            "question_metadata": new_question_metadata,
            "responses": updated_responses
        }
        
        # Save transformed data
        output_path = os.path.join('preprocessed_data', 'self-repoted-mental-health-college-students-2022', 'transformed_data.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(transformed_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Transformed data saved to: {output_path}")
        print(f"Total questions: {len(new_question_metadata)}")
        print(f"Total responses: {len(updated_responses)}")
        
        # Show examples of transformations
        print("\nExample transformations:")
        for i, (old_key, new_key) in enumerate(list(old_to_new_mapping.items())[:5]):
            if old_key != new_key:
                print(f"  '{old_key}' → '{new_key}'")
        
        return output_path
        
    except FileNotFoundError:
        print(f"Error: File not found at {input_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    transform_questionnaire() 