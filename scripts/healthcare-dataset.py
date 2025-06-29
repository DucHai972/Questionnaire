import pandas as pd
import json
import os
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def generate_html_questionnaire(questionnaire, output_dir):
    # Add questions
    html_content = f"<div class=\"question\">"
    for q_id, question in questionnaire['question_metadata'].items():
        html_content += f"""<div class="question-id">{q_id}</div>
        <div class="question-text">{question}</div>
"""
    
    html_content += "</div>"
    # Add responses
    html_content += """
    <h2>Responses</h2>
    <div class="responses">
"""
    
    for response in questionnaire['responses']:  
        html_content += f"""
        <div class="response">
            <div class="respondent-id">Respondent: {response['respondent']}</div>
"""
        for q_id, answer in response['answers'].items():
            html_content += f"""            <div class="answer">{q_id}: {answer}</div>
"""
        html_content += "        </div>\n"
    
    html_content += """
    </div>
"""
    
    output_path = os.path.join(output_dir, 'healthcare_questionnaire.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path

def generate_xml_questionnaire(questionnaire, output_dir):
    """Generate XML format questionnaire"""
    root = Element('questionnaire')
    
    # Add metadata
    metadata = SubElement(root, 'question_metadata')
    for q_id, question in questionnaire['question_metadata'].items():
        question_elem = SubElement(metadata, 'question')
        question_elem.set('id', q_id)
        question_elem.text = question
    
    # Add responses
    responses = SubElement(root, 'responses')
    for response in questionnaire['responses']:
        response_elem = SubElement(responses, 'response')
        response_elem.set('respondent', response['respondent'])
        
        for q_id, answer in response['answers'].items():
            answer_elem = SubElement(response_elem, 'answer')
            answer_elem.set('question_id', q_id)
            answer_elem.text = str(answer)
    
    # Pretty print XML
    rough_string = tostring(root, 'unicode')
    reparsed = minidom.parseString(rough_string)
    
    output_path = os.path.join(output_dir, 'healthcare_questionnaire.xml')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(reparsed.toprettyxml(indent="  "))
    
    return output_path

def generate_markdown_questionnaire(questionnaire, output_dir):
    """Generate Markdown format questionnaire"""
    md_content = ""
    
    # Add questions
    md_content += "## Questions\n\n"
    for q_id, question in questionnaire['question_metadata'].items():
        md_content += f"### {q_id}\n{question}\n\n"
    
    # Add sample responses
    for i, response in enumerate(questionnaire['responses']):  # Show first 5 responses
        md_content += f"### Respondent {response['respondent']}\n"
        for q_id, answer in response['answers'].items():
            md_content += f"- **{q_id}**: {answer}\n"
        md_content += "\n"
    
    output_path = os.path.join(output_dir, 'healthcare_questionnaire.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return output_path

def generate_raw_text_questionnaire(questionnaire, output_dir):
    """Generate Raw text format questionnaire"""
    # Add questions
    text_content = "QUESTIONS:\n"
    text_content += "-" * 20 + "\n"
    for q_id, question in questionnaire['question_metadata'].items():
        text_content += f"{q_id}: {question}\n\n"
    
    # Add sample responses
    text_content += "\nSAMPLE RESPONSES:\n"
    text_content += "-" * 20 + "\n"
    for response in questionnaire['responses']:  # Show first 5 responses
        text_content += f"Respondent: {response['respondent']}\n"
        for q_id, answer in response['answers'].items():
            text_content += f"  {q_id}: {answer}\n"
        text_content += "\n"
    
    output_path = os.path.join(output_dir, 'healthcare_questionnaire.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    return output_path

def create_questionnaire_from_csv():
    # Path to the CSV file
    csv_path = os.path.join('data', 'healthcare-dataset', 'healthcare_dataset.csv')
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_path)
        if 'Billing Amount' in df.columns:
            df['Billing Amount'] = df['Billing Amount'].apply(lambda x: round(x) if pd.notna(x) else x)
            print("Billing Amount column values have been rounded.")
            
        print("Converting healthcare dataset to questionnaire format...")
        print("=" * 60)
        
        question_metadata = {}
        column_mappings = {}  # Store mappings for MCQ columns
        
        # Analyze each column and create questions
        for column in df.columns:
            distinct_values = df[column].dropna().unique()
            distinct_count = len(distinct_values)
            question_id = f"{column}"
            
            print(f"Column: {column} | Distinct values: {distinct_count}")
            
            if distinct_count < 10:
                # Create MCQ question
                options = []
                value_to_letter = {}
                
                for i, value in enumerate(sorted(distinct_values)):
                    letter = chr(65 + i)  # A, B, C, D, etc.
                    options.append(f"{letter}. {value}")
                    value_to_letter[value] = letter.lower()
                
                question_text = f"What is your {column.lower()}? {' '.join(options)}"
                question_metadata[question_id] = question_text
                column_mappings[column] = value_to_letter
                
            else:
                # Create open-ended question
                question_text = f"What is your {column.lower()}? (Open-ended)"
                question_metadata[question_id] = question_text
                column_mappings[column] = None  # No mapping needed for open-ended
        
        # Create responses
        responses = []
        for index, row in df.iterrows():
            respondent_id = f"{index + 1}"
            answers = {}
            
            for column in df.columns:
                question_id = f"{column}"
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
        output_dir = os.path.join('preprocessed_data', 'healthcare-dataset')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate all formats
        print(f"\nGenerating questionnaire in multiple formats...")
        
        # JSON format
        json_path = os.path.join(output_dir, 'healthcare_questionnaire.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(questionnaire, f, indent=2, ensure_ascii=False)
        print(f"✓ JSON saved to: {json_path}")
        
        # HTML format
        html_path = generate_html_questionnaire(questionnaire, output_dir)
        print(f"✓ HTML saved to: {html_path}")
        
        # XML format
        xml_path = generate_xml_questionnaire(questionnaire, output_dir)
        print(f"✓ XML saved to: {xml_path}")
        
        # Markdown format
        md_path = generate_markdown_questionnaire(questionnaire, output_dir)
        print(f"✓ Markdown saved to: {md_path}")
        
        # Raw text format
        txt_path = generate_raw_text_questionnaire(questionnaire, output_dir)
        print(f"✓ Raw text saved to: {txt_path}")
        
        print(f"\nQuestionnaire created successfully in all formats!")
        print(f"Total questions: {len(question_metadata)}")
        print(f"Total responses: {len(responses)}")
        
        # Print sample of question metadata
        print("\nSample Questions:")
        print("-" * 40)
        for i, (q_id, question) in enumerate(list(question_metadata.items())[:3]):
            print(f"{q_id}: {question}")
        
        return questionnaire
        
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        print("Please make sure the file exists in the correct location.")
    except Exception as e:
        print(f"Error processing the file: {str(e)}")

if __name__ == "__main__":
    create_questionnaire_from_csv()