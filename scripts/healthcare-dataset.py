import pandas as pd
import json
import os
import argparse
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import re

def generate_html_questionnaire(questionnaire, output_dir):
    # Add questions section
    html_content = "<h1>Questions</h1>\n<ul>\n"
    
    for q_id, question in questionnaire['question_metadata'].items():
        html_content += f"  <li><strong>{q_id}:</strong> {question}</li>\n"
    
    html_content += "</ul>\n\n"
    
    # Add responses section
    html_content += "<h1>Responses</h1>\n"
    
    for response in questionnaire['responses']:  
        html_content += f"<h2>Respondent {response['respondent']}</h2>\n"
        html_content += "<ul>\n"
        
        # Get all question IDs to ensure we show missing answers
        all_question_ids = questionnaire['question_metadata'].keys()
        
        for q_id in all_question_ids:
            if q_id in response['answers']:
                answer = response['answers'][q_id]
                html_content += f"  <li><strong>{q_id}:</strong> {answer}</li>\n"
            else:
                html_content += f"  <li><strong>{q_id}:</strong> (missing)</li>\n"
    
        html_content += "</ul>\n\n"
    
    output_path = os.path.join(output_dir, 'healthcare_questionnaire.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path

def generate_xml_questionnaire(questionnaire, output_dir):
    """Generate XML format questionnaire with structured questions and responses."""
    root = Element('questionnaire')
    
    # Helper function to parse question details
    def parse_question_xml(q_id, question):
        """Parse question description to extract type and details for XML."""
        if "[Open-ended]" in question:
            return "open-ended", question.replace("[Open-ended]", "").strip(), None
        elif "[MCQ:" in question:
            # Extract main question and MCQ options
            main_part = question.split("[MCQ:")[0].strip()
            mcq_part = question.split("[MCQ:")[1].replace("]", "").strip()
            
            # Parse MCQ options using split-based approach
            options = {}
            parts = mcq_part.split(' ')
            i = 0
            while i < len(parts):
                if i < len(parts) - 1 and parts[i].endswith('.'):
                    letter = parts[i][0].lower()
                    value = parts[i+1]
                    options[letter] = value
                    i += 2
                else:
                    i += 1
            
            return "mcq", main_part, options
        else:
            return "unknown", question, None
    
    # Add Questions section
    questions_elem = SubElement(root, 'questions')
    
    for q_id, question in questionnaire['question_metadata'].items():
        question_type, question_text, options = parse_question_xml(q_id, question)
        
        # Create question element
        question_elem = SubElement(questions_elem, 'question')
        
        # Clean ID for XML
        xml_id = q_id.replace(" ", "_").replace("(", "").replace(")", "").lower()
        question_elem.set('id', xml_id)
        question_elem.set('type', question_type)
        question_elem.text = question_text
        
        # Add scale for MCQ questions
        if options:
            scale_elem = SubElement(question_elem, 'scale')
            for value, desc in options.items():
                option_elem = SubElement(scale_elem, 'option')
                option_elem.set('value', value)
                option_elem.text = desc
    
    # Add Responses section
    responses_elem = SubElement(root, 'responses')
    
    for response in questionnaire['responses']:
        respondent_elem = SubElement(responses_elem, 'respondent')
        respondent_elem.set('id', response['respondent'])
        
        for q_id, answer in response['answers'].items():
            # Clean key for XML element name
            xml_key = q_id.replace(" ", "_").replace("(", "").replace(")", "").lower()
            field_elem = SubElement(respondent_elem, xml_key)
            field_elem.text = str(answer)
    
    # Pretty print XML
    rough_string = tostring(root, 'unicode')
    reparsed = minidom.parseString(rough_string)
    
    output_path = os.path.join(output_dir, 'healthcare_questionnaire.xml')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(reparsed.toprettyxml(indent="  "))
    
    return output_path

def generate_markdown_questionnaire(questionnaire, output_dir):
    """Generate Markdown format questionnaire"""
    # Add questions
    md_content = "## Questions\n\n"
    for q_id, question in questionnaire['question_metadata'].items():
        md_content += f"- **{q_id}:** {question}\n"
    md_content += "\n"
    
    # Add sample responses
    md_content += "## Responses\n\n"
    for i, response in enumerate(questionnaire['responses']):  # Show first 5 responses
        md_content += f"### Respondent {response['respondent']}\n\n"
        for q_id, answer in response['answers'].items():
            md_content += f"- **{q_id}:** {answer}\n"
        md_content += "\n"
    
    output_path = os.path.join(output_dir, 'healthcare_questionnaire.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    return output_path

def generate_raw_text_questionnaire(questionnaire, output_dir):
    """Generate Raw text format questionnaire with structured questions and responses."""
    
    # Helper function to parse question details
    def parse_question_txt(question):
        """Parse question description to extract type and details for TXT."""
        if "[Open-ended]" in question:
            return "open-ended", question.replace("[Open-ended]", "").strip(), None
        elif "[MCQ:" in question:
            # Extract main question and MCQ options
            main_part = question.split("[MCQ:")[0].strip()
            mcq_part = question.split("[MCQ:")[1].replace("]", "").strip()
            
            # Parse MCQ options using split-based approach
            options = []
            parts = mcq_part.split(' ')
            i = 0
            while i < len(parts):
                if i < len(parts) - 1 and parts[i].endswith('.'):
                    letter = parts[i][0].lower()
                    value = parts[i+1]
                    options.append(f"     {letter} = {value}")
                    i += 2
                else:
                    i += 1
            
            return "mcq", main_part, options
        else:
            return "unknown", question, None
    
    # Add questions section
    text_content = "Questions:\n"
    
    question_num = 1
    for q_id, question in questionnaire['question_metadata'].items():
        question_type, question_text, options = parse_question_txt(question)
        
        if question_type == "open-ended":
            text_content += f"{question_num}. {q_id}: {question_text} (Open-ended)\n"
        elif question_type == "mcq" and options:
            text_content += f"{question_num}. {q_id}: {question_text}\n"
            text_content += "   MCQ options:\n"
            for option in options:
                text_content += f"{option}\n"
        else:
            text_content += f"{question_num}. {q_id}: {question_text}\n"
        
        question_num += 1
    
    # Add responses section
    text_content += "\nResponses:\n"
    
    for response in questionnaire['responses']:
        text_content += f"Respondent {response['respondent']}:\n"
        for q_id, answer in response['answers'].items():
            text_content += f"- {q_id}: {answer}\n"
        text_content += "\n"
    
    output_path = os.path.join(output_dir, 'healthcare_questionnaire.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    return output_path

def create_questionnaire_from_csv(formats_to_generate=None):
    """
    Create questionnaire from CSV file and generate specified formats
    
    Args:
        formats_to_generate (list): List of formats to generate ['json', 'html', 'xml', 'markdown', 'txt']
                                  If None, generates all formats
    """
    if formats_to_generate is None:
        formats_to_generate = ['json', 'html', 'xml', 'markdown', 'txt']
    
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
                
                question_text = f"What is your {column.lower()}? [MCQ: {' '.join(options)}]"
                question_metadata[question_id] = question_text
                column_mappings[column] = value_to_letter
                
            else:
                # Create open-ended question
                question_text = f"What is your {column.lower()}? [Open-ended]"
                question_metadata[question_id] = question_text
                column_mappings[column] = None  # No mapping needed for open-ended
        
        # Create responses
        responses = []
        for idx, (index, row) in enumerate(df.iterrows()):
            respondent_id = f"{idx + 1}"
            answers = {}
            
            for column in df.columns:
                question_id = f"{column}"
                value = row[column]
                
                if value is None or (isinstance(value, (int, float)) and pd.isna(value)) or str(value).lower() == 'nan':
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
        
        # Generate requested formats
        print(f"\nGenerating questionnaire in requested formats: {', '.join(formats_to_generate)}")
        
        generated_files = []
        
        if 'json' in formats_to_generate:
        # JSON format
            json_path = os.path.join(output_dir, 'healthcare_questionnaire.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(questionnaire, f, indent=2, ensure_ascii=False)
            print(f"✓ JSON saved to: {json_path}")
            generated_files.append(json_path)
        
        if 'html' in formats_to_generate:
        # HTML format
            html_path = generate_html_questionnaire(questionnaire, output_dir)
            print(f"✓ HTML saved to: {html_path}")
            generated_files.append(html_path)
        
        if 'xml' in formats_to_generate:
        # XML format
            xml_path = generate_xml_questionnaire(questionnaire, output_dir)
            print(f"✓ XML saved to: {xml_path}")
            generated_files.append(xml_path)
        
        if 'markdown' in formats_to_generate:
        # Markdown format
            md_path = generate_markdown_questionnaire(questionnaire, output_dir)
            print(f"✓ Markdown saved to: {md_path}")
            generated_files.append(md_path)
        
        if 'txt' in formats_to_generate:
        # Raw text format
            txt_path = generate_raw_text_questionnaire(questionnaire, output_dir)
            print(f"✓ Raw text saved to: {txt_path}")
            generated_files.append(txt_path)
        
        print(f"\nQuestionnaire created successfully!")
        print(f"Generated {len(generated_files)} file(s)")
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

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Convert healthcare dataset to questionnaire formats')
    
    parser.add_argument('--html', action='store_true', help='Generate HTML format')
    parser.add_argument('--json', action='store_true', help='Generate JSON format')
    parser.add_argument('--xml', action='store_true', help='Generate XML format')
    parser.add_argument('--markdown', action='store_true', help='Generate Markdown format')
    parser.add_argument('--txt', action='store_true', help='Generate raw text format')
    parser.add_argument('--all', action='store_true', help='Generate all formats')
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Determine which formats to generate
    formats_to_generate = []
    
    if args.all:
        formats_to_generate = ['json', 'html', 'xml', 'markdown', 'txt']
    else:
        if args.json:
            formats_to_generate.append('json')
        if args.html:
            formats_to_generate.append('html')
        if args.xml:
            formats_to_generate.append('xml')
        if args.markdown:
            formats_to_generate.append('markdown')
        if args.txt:
            formats_to_generate.append('txt')
    
    # If no specific format is requested, generate all formats
    if not formats_to_generate:
        print("No specific format requested. Generating all formats...")
        formats_to_generate = ['json', 'html', 'xml', 'markdown', 'txt']
    
    create_questionnaire_from_csv(formats_to_generate)