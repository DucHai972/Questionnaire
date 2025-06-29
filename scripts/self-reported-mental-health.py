import pandas as pd
import json
import os

def create_questionnaire_from_excel():
    # Path to the Excel file
    excel_path = os.path.join('data', 'self-reported-mental-health-college-students-2022', 'Raw data.xlsx')
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_path)
        
        print("Converting mental health dataset to questionnaire format...")
        print("=" * 60)
        print(f"Total rows: {len(df)}")
        print(f"Total columns: {len(df.columns)}")
        
        question_metadata = {}
        column_mappings = {}  # Store mappings for MCQ columns
        
        # Analyze each column and create questions
        for column in df.columns:
            # Clean column names by removing extra spaces and special characters
            clean_column = str(column).strip()
            distinct_values = df[column].dropna().unique()
            distinct_count = len(distinct_values)
            question_id = f"{clean_column}"
            
            print(f"Column: {clean_column} | Distinct values: {distinct_count}")
            
            if distinct_count < 10:
                # Create MCQ question
                options = []
                value_to_letter = {}
                
                # Convert all values to strings before sorting to handle mixed types
                sorted_values = sorted(distinct_values, key=lambda x: str(x))
                
                for i, value in enumerate(sorted_values):
                    letter = chr(65 + i)  # A, B, C, D, etc.
                    options.append(f"{letter}. {value}")
                    value_to_letter[value] = letter.lower()
                
                question_text = f"What is your {clean_column.lower()}? {' '.join(options)}"
                question_metadata[question_id] = question_text
                column_mappings[column] = value_to_letter
                
            else:
                # Create open-ended question
                question_text = f"What is your {clean_column.lower()}? (Open-ended)"
                question_metadata[question_id] = question_text
                column_mappings[column] = None  # No mapping needed for open-ended
        
        # Create responses
        responses = []
        for index, row in df.iterrows():
            respondent_id = f"{index + 1}"
            answers = {}
            
            for column in df.columns:
                clean_column = str(column).strip()
                question_id = f"{clean_column}"
                value = row[column]
                
                if pd.isna(value):
                    continue  # Skip NaN values
                
                if column_mappings[column] is not None:
                    # MCQ - convert to letter
                    answers[question_id] = column_mappings[column].get(value, str(value))
                else:
                    # Open-ended - keep original value
                    answers[question_id] = str(value)
            
            responses.append({
                "respondent": respondent_id,
                "answers": answers
            })
        
        # Create final questionnaire structure
        questionnaire = {
            "question_metadata": question_metadata,
            "responses": responses
        }
        
        # Create output directory
        output_dir = os.path.join('preprocessed_data', 'self-repoted-mental-health-college-students-2022')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate JSON format only
        json_path = os.path.join(output_dir, 'mental_health_questionnaire.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(questionnaire, f, indent=2, ensure_ascii=False)
        
        print(f"\nQuestionnaire created successfully!")
        print(f"JSON saved to: {json_path}")
        print(f"Total questions: {len(question_metadata)}")
        print(f"Total responses: {len(responses)}")
        
        # Print sample of question metadata
        print("\nSample Questions:")
        print("-" * 40)
        for i, (q_id, question) in enumerate(list(question_metadata.items())[:3]):
            print(f"{q_id}: {question}")
        
        return questionnaire
        
    except FileNotFoundError:
        print(f"Error: File not found at {excel_path}")
        print("Please make sure the Excel file exists in the correct location.")
    except Exception as e:
        print(f"Error processing the file: {str(e)}")

if __name__ == "__main__":
    create_questionnaire_from_excel()
