import pandas as pd
import json
import os
import re

def clean_text(text):
    """Clean text by removing tabs and extra whitespace"""
    if text is None:
        return None
    if isinstance(text, str):
        # Remove tabs and normalize whitespace
        text = re.sub(r'\t+', ' ', str(text))
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    return text

def parse_question_info(question_text):
    """Parse question number and content from question text"""
    if not isinstance(question_text, str):
        return None, question_text
    
    # Match patterns like "1.", "5.1", "16.2", etc.
    match = re.match(r'^(\d+(?:\.\d+)?)\s*\.?\s*(.*)', question_text.strip())
    if match:
        question_num = match.group(1)
        question_content = match.group(2).strip()
        return question_num, question_content
    return None, question_text

def create_question_structure(columns):
    """Create question structure with metadata and answer mapping"""
    question_metadata = {}
    answer_mapping = {}
    
    # Group questions by base number
    question_groups = {}
    
    for original_col in columns:
        q_num, q_content = parse_question_info(original_col)
        
        if q_num:
            base_num = q_num.split('.')[0]
            
            if base_num not in question_groups:
                question_groups[base_num] = {
                    'base_question': '',
                    'sub_questions': {},
                    'original_columns': []
                }
            
            question_groups[base_num]['original_columns'].append(original_col)
            
            if '.' in q_num:
                # Sub-question like 5.1, 5.2
                sub_num = q_num.split('.')[1]
                
                # Extract main question and identifier
                words = q_content.split()
                if words:
                    # Try to identify the specific part (Father, Mother, etc.)
                    if len(words) > 1:
                        potential_identifier = words[-1]
                        if potential_identifier.lower() in ['father', 'mother'] or len(potential_identifier) < 20:
                            main_question = ' '.join(words[:-1])
                            identifier = potential_identifier
                        else:
                            main_question = q_content
                            identifier = f"part {sub_num}"
                    else:
                        main_question = q_content
                        identifier = f"part {sub_num}"
                    
                    # Update base question if this one is more complete
                    if not question_groups[base_num]['base_question'] or len(main_question) > len(question_groups[base_num]['base_question']):
                        question_groups[base_num]['base_question'] = main_question
                    
                    sub_key = f"Q{q_num} {identifier}"
                    question_groups[base_num]['sub_questions'][sub_key] = f"{identifier}?"
                    answer_mapping[original_col] = (f"Q{base_num}", f"Q{q_num}")
                else:
                    question_groups[base_num]['base_question'] = q_content
                    question_groups[base_num]['is_single'] = True
                    answer_mapping[original_col] = (f"Q{q_num}", None)
            else:
                # Single question
                question_groups[base_num]['base_question'] = q_content
                question_groups[base_num]['is_single'] = True
                answer_mapping[original_col] = (f"Q{q_num}", None)
        else:
            # No question number found
            col_idx = columns.index(original_col) + 1
            answer_mapping[original_col] = (f"Column_{col_idx}", None)
    
    # Create final metadata structure
    for base_num, group_info in question_groups.items():
        if group_info.get('is_single'):
            # Single question: "Q1. Year of birth": "What is your date of birth?"
            # Create a shorter, cleaner title
            title_words = group_info['base_question'].split()[:3]  # Take first 3 words for title
            title = ' '.join(title_words)
            if title.endswith(':'):
                title = title[:-1]  # Remove trailing colon
            
            key = f"Q{base_num}. {title}"
            question_metadata[key] = group_info['base_question']
        else:
            # Multiple questions: create group structure
            # Create title from base question
            title_words = group_info['base_question'].split()[:2]  # Take first 2 words
            title = ' '.join(title_words)
            
            key = f"Q{base_num}. {title}"
            question_metadata[key] = {
                "base_question": group_info['base_question'],
                "sub_questions": group_info['sub_questions']
            }
        
        # Update answer mapping with cleaner keys
        for original_col in group_info['original_columns']:
            old_key, sub_key = answer_mapping[original_col]
            if group_info.get('is_single'):
                answer_mapping[original_col] = (key, None)
            else:
                answer_mapping[original_col] = (key, sub_key)
    
    return question_metadata, answer_mapping

def convert_row_to_structured_format(row, answer_mapping):
    """Convert a data row to the structured format"""
    structured_row = {}
    
    for original_col, value in row.items():
        if value is None:
            continue
            
        main_key, sub_key = answer_mapping.get(original_col, (original_col, None))
        
        if sub_key is None:
            # Single question
            structured_row[main_key] = value
        else:
            # Grouped question
            if main_key not in structured_row:
                structured_row[main_key] = {}
            structured_row[main_key][sub_key] = value
    
    return structured_row

def convert_excel_to_json():
    """Convert Excel data to JSON format with clean question structure"""
    # Path to the Excel file
    excel_path = os.path.join('data', 'self-reported-mental-health-college-students-2022', 'Raw data.xlsx')
    
    try:
        # Read the Excel file to examine its structure
        print("Reading Excel file...")
        
        df_preview = pd.read_excel(excel_path, nrows=10)
        print("Preview of first few rows:")
        print(df_preview.head())
        
        df_no_header = pd.read_excel(excel_path, header=None)
        
        # Find the row with actual questions
        best_df = None
        for row_idx in range(min(5, len(df_no_header))):
            row_data = df_no_header.iloc[row_idx]
            meaningful_text_count = sum(1 for val in row_data if isinstance(val, str) and len(str(val).strip()) > 3)
            
            print(f"Row {row_idx}: Meaningful text={meaningful_text_count}")
            
            if meaningful_text_count > len(df_no_header.columns) * 0.3:
                questions = []
                for i, val in enumerate(row_data):
                    if pd.notna(val) and isinstance(val, str) and len(str(val).strip()) > 0:
                        question = clean_text(str(val))
                        questions.append(question)
                    else:
                        questions.append(f"Column_{i+1}")
                
                best_df = pd.read_excel(excel_path, header=None, skiprows=row_idx+1)
                best_df.columns = questions
                break
        
        if best_df is None:
            best_df = pd.read_excel(excel_path, header=1)
        
        df = best_df
        
        print(f"\nSuccessfully loaded data with {len(df)} rows and {len(df.columns)} columns")
        
        # Create question structure
        print("Creating question structure...")
        question_metadata, answer_mapping = create_question_structure(list(df.columns))
        
        print("Question structure created:")
        for key, value in list(question_metadata.items())[:5]:
            if isinstance(value, dict):
                print(f"  {key}: [grouped question with {len(value['sub_questions'])} parts]")
            else:
                print(f"  {key}: {value[:50]}...")
        
        # Convert data
        data = {
            "question_metadata": question_metadata,
            "responses": []
        }
        
        print("Processing responses...")
        for idx, (_, row) in enumerate(df.iterrows()):
            # Clean the row data first
            cleaned_row = {}
            for column in df.columns:
                value = row[column]
                if value is None or (isinstance(value, (int, float)) and pd.isna(value)) or str(value).lower() == 'nan':
                    cleaned_row[column] = None
                else:
                    cleaned_row[column] = clean_text(value)
            
            # Convert to structured format
            structured_row = convert_row_to_structured_format(cleaned_row, answer_mapping)
            
            response = {
                "respondent": str(idx + 1),
                "answers": structured_row
            }
            data["responses"].append(response)
        
        # Create output directory
        output_dir = os.path.join('preprocessed_data', 'self-repoted-mental-health-college-students-2022')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to JSON file
        json_path = os.path.join(output_dir, 'raw_data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ JSON saved to: {json_path}")
        print(f"Total responses: {len(data['responses'])}")
        print(f"Question structure: Clean format with grouped questions")
        
        return json_path
        
    except FileNotFoundError:
        print(f"Error: File not found at {excel_path}")
        print("Please make sure the file exists in the correct location.")
    except Exception as e:
        print(f"Error processing the file: {str(e)}")

if __name__ == "__main__":
    convert_excel_to_json()
