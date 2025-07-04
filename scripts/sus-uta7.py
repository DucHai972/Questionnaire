import pandas as pd
import json
import os
import argparse
from pathlib import Path
import re

def load_and_combine_csv_files():
    """Load both SUS CSV files and combine them"""
    try:
        # Load both CSV files
        current_df = pd.read_csv('data/sus-uta7/sus_current.csv')
        assistant_df = pd.read_csv('data/sus-uta7/sus_assistant.csv')
        
        print(f"✓ Loaded sus_current.csv: {len(current_df)} responses")
        print(f"✓ Loaded sus_assistant.csv: {len(assistant_df)} responses")
        
        # Add a source column to distinguish between datasets
        current_df['dataset'] = 'current'
        assistant_df['dataset'] = 'assistant'
        
        # Combine both dataframes
        combined_df = pd.concat([current_df, assistant_df], ignore_index=True)
        
        print(f"✓ Combined total responses: {len(combined_df)}")
        
        return combined_df
        
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return None

def create_json_structure(df):
    """Convert DataFrame to the specified JSON structure"""
    
    # Define the questions with proper type indicators in square brackets
    questions = {
        "name": "Name of the respondent [Open-ended]",
        "group": "Group of the respondent [MCQ: A. Senior B. Junior C. Middle D. Intern]",
        "Frequent usage": "I think that I would like to use this system frequently. [Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]",
        "System complexity": "I found the system unnecessarily complex. [Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]",
        "Ease of use": "I thought the system was easy to use. [Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]",
        "Need for technical support": "I think that I would need the support of a technical person to be able to use this system. [Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]",
        "Integration of functions": "I found the various functions in this system were well integrated. [Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]",
        "Inconsistency": "I thought there was too much inconsistency in this system. [Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]",
        "Ease of learning": "I would imagine that most people would learn to use this system very quickly. [Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]",
        "Cumbersome to use": "I found the system very awkward to use. [Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]",
        "Confidence in use": "I felt very confident using the system. [Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]",
        "Need to learn before use": "I needed to learn a lot of things before I could get going with this system. [Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]"
    }
    
    # Group mapping from text to letter codes
    group_mapping = {
        'senior': 'A',
        'junior': 'B', 
        'middle': 'C',
        'intern': 'D'
    }
    
    # SUS question mapping from column names to friendly names
    sus_mapping = {
        'sus_01': 'Frequent usage',
        'sus_02': 'System complexity',
        'sus_03': 'Ease of use',
        'sus_04': 'Need for technical support',
        'sus_05': 'Integration of functions',
        'sus_06': 'Inconsistency',
        'sus_07': 'Ease of learning',
        'sus_08': 'Cumbersome to use',
        'sus_09': 'Confidence in use',
        'sus_10': 'Need to learn before use'
    }
    
    # Create responses array
    responses = []
    
    print("Processing responses...")
    for index, row in df.iterrows():
        # Convert group to letter code
        group_code = group_mapping.get(row['group'].lower(), row['group'])
        
        response = {
            "answers": {
                "name": row['name'],
                "group": group_code
            }
        }
        
        # Add SUS responses with mapped names
        for sus_col, friendly_name in sus_mapping.items():
            response["answers"][friendly_name] = int(row[sus_col])
        
        responses.append(response)
        
        if (index + 1) % 20 == 0:
            print(f"  Processed {index + 1} responses...")
    
    # Create the final JSON structure (top-level questions and responses)
    json_data = {
        "questions": questions,
        "responses": responses
    }
    
    print(f"✓ Created JSON structure with {len(responses)} responses")
    
    return json_data

def save_json_file(json_data, output_dir):
    """Save JSON data to file"""
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Save JSON file
        json_path = os.path.join(output_dir, 'sus_uta7_questionnaire.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        # Calculate file size
        file_size = os.path.getsize(json_path) / 1024  # KB
        
        print(f"✓ JSON saved to: {json_path}")
        print(f"✓ Total responses: {len(json_data['responses'])}")
        print(f"✓ File size: {file_size:.1f} KB")
        
        return json_path
        
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return None

def convert_sus_to_json():
    """Main function to convert SUS CSV files to JSON"""
    print("=== SUS-UTA7 CSV to JSON Converter ===\n")
    
    # Load and combine CSV files
    df = load_and_combine_csv_files()
    if df is None:
        return None
    
    print(f"\n=== Data Summary ===")
    print(f"Total responses: {len(df)}")
    print(f"Datasets: {df['dataset'].value_counts().to_dict()}")
    print(f"Groups: {df['group'].value_counts().to_dict()}")
    
    # Create JSON structure
    print(f"\n=== Converting to JSON ===")
    json_data = create_json_structure(df)
    
    # Save JSON file
    print(f"\n=== Saving File ===")
    output_dir = os.path.join('preprocessed_data', 'sus-uta7')
    json_path = save_json_file(json_data, output_dir)
    
    return json_path

def convert_json_to_html(json_path, output_dir):
    """Convert JSON data to HTML format matching the specified structure"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Start HTML content
        html_content = "<h1>Questions</h1>\n<ul>\n"
        
        # Define Likert scale questions for special formatting
        likert_questions = {
            "Frequent usage", "System complexity", "Ease of use", 
            "Need for technical support", "Integration of functions", 
            "Inconsistency", "Ease of learning", "Cumbersome to use", 
            "Confidence in use", "Need to learn before use"
        }
        
        # Add questions section with special formatting for Likert questions
        for question_key, question_desc in data['questions'].items():
            if question_key in likert_questions:
                # Format Likert scale questions with scale notation
                formatted_desc = question_desc.replace("[Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]", "(Rate from 1 to 5, where 1 = strongly disagree, 5 = strongly agree)")
                formatted_desc = formatted_desc.replace("[Likert 1–5: 1 = Strongly Disagree, 5 = Strongly Agree]", "(Rate from 1 to 5)")
                if "(Rate" not in formatted_desc:
                    formatted_desc += " (Rate from 1 to 5)"
                html_content += f"  <li><strong>{question_key}:</strong> {formatted_desc}</li>\n"
            else:
                # Regular questions
                html_content += f"  <li><strong>{question_key}:</strong> {question_desc}</li>\n"
        
        html_content += "</ul>\n\n"
        
        # Add responses section
        html_content += "<h1>Responses</h1>\n"
        
        for i, response in enumerate(data['responses']):
            html_content += f"<h2>Respondent {i + 1}</h2>\n"
            html_content += "<ul>\n"
            
            # Get all question keys to ensure we show missing answers
            all_question_keys = data['questions'].keys()
            
            for question_key in all_question_keys:
                if question_key in response['answers']:
                    answer_value = response['answers'][question_key]
                    
                    if answer_value is not None and answer_value != "":
                        html_content += f"  <li><strong>{question_key}:</strong> {answer_value}</li>\n"
                    else:
                        html_content += f"  <li><strong>{question_key}:</strong> (missing)</li>\n"
                else:
                    html_content += f"  <li><strong>{question_key}:</strong> (missing)</li>\n"
            
            html_content += "</ul>\n\n"
        
        # Save HTML file
        html_path = os.path.join(output_dir, 'sus_uta7_questionnaire.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML saved to: {html_path}")
        return html_path
        
    except Exception as e:
        print(f"Error creating HTML: {e}")
        return None

def convert_json_to_xml(json_path, output_dir):
    """Convert JSON data to structured XML format with detailed question elements."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<questionnaire>\n'
        
        # Add Questions section
        xml_content += '  <questions>\n'
        
        # Helper function to convert to camelCase
        def to_camel_case(text):
            words = text.replace("-", " ").replace("_", " ").split()
            return words[0].lower() + ''.join(word.capitalize() for word in words[1:])
        
        # Helper function to extract MCQ options
        def extract_mcq_options(text):
            opt_match = re.search(r'MCQ: (.+?)\]', text)
            if not opt_match:
                return []
            opts = opt_match.group(1)
            return re.findall(r'([A-Z])\. ([^A-Z]+?)(?=(?:[A-Z]\.|$))', opts)
        
        # Helper function to extract Likert scale
        def extract_likert_scale(text):
            scale_match = re.search(r'Likert (\d+)–(\d+)', text)
            if scale_match:
                start, end = scale_match.groups()
                return f"{start}-{end}"
            return None
        
        # Process questions
        for question_key, question_desc in data['questions'].items():
            # Generate question ID
            q_id = to_camel_case(question_key)
            
            # Extract question type and text
            type_match = re.search(r'\[(.*?)\]', question_desc)
            if type_match:
                type_str = type_match.group(1)
                q_text = question_desc.split('[')[0].strip()
            else:
                type_str = "Open-ended"
                q_text = question_desc
            
            # Clean up question text
            if question_key == "name":
                q_text = "Name of the respondent"
            elif question_key == "group":
                q_text = "Group of the respondent"
            else:
                # Remove any scale information from the question text
                q_text = re.sub(r'\(Rate.*?\)', '', q_text).strip()
                q_text = re.sub(r'\(.*?=.*?\)', '', q_text).strip()
            
            if "MCQ" in type_str:
                # MCQ question with options
                xml_content += f'    <question id="{q_id}" type="mcq">{q_text}\n'
                options = extract_mcq_options(question_desc)
                for letter, val in options:
                    xml_content += f'      <option value="{letter}">{val.strip()}</option>\n'
                xml_content += '    </question>\n'
            elif "Likert" in type_str:
                # Likert question with scale
                scale = extract_likert_scale(type_str)
                if scale:
                    xml_content += f'    <question id="{q_id}" type="likert" scale="{scale}">{q_text}</question>\n'
                else:
                    xml_content += f'    <question id="{q_id}" type="likert" scale="1-5">{q_text}</question>\n'
            else:
                # Open-ended question
                xml_content += f'    <question id="{q_id}" type="open-ended">{q_text}</question>\n'
        
        xml_content += '  </questions>\n'
        
        # Add Responses section
        xml_content += '  <responses>\n'
        
        for i, response in enumerate(data['responses']):
            xml_content += f'    <respondent id="{i+1}">\n'
            
            for answer_key, answer_value in response['answers'].items():
                # Convert key to camelCase for XML
                xml_key = to_camel_case(answer_key)
                
                # Handle single answers
                xml_content += f'      <{xml_key}>{answer_value}</{xml_key}>\n'
            
            xml_content += '    </respondent>\n'
        
        xml_content += '  </responses>\n'
        xml_content += '</questionnaire>\n'
        
        # Save XML file
        xml_path = os.path.join(output_dir, 'sus_uta7_questionnaire.xml')
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"✓ XML saved to: {xml_path}")
        return xml_path
        
    except Exception as e:
        print(f"Error creating XML: {e}")
        return None

def convert_json_to_markdown(json_path, output_dir):
    """Convert JSON data to simple Markdown format"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Add questions
        md_content = "## Questions\n\n"
        for question_key, question_desc in data['questions'].items():
            md_content += f"- **{question_key}:** {question_desc}\n"
        md_content += "\n"
        
        # Add responses
        md_content += "## Responses\n\n"
        for i, response in enumerate(data['responses']):
            md_content += f"### Respondent {i + 1}\n\n"
            
            for answer_key, answer_value in response['answers'].items():
                if answer_value is not None:
                    md_content += f"- **{answer_key}:** {answer_value}\n"
                else:
                    md_content += f"- **{answer_key}:** *No answer*\n"
            md_content += "\n"
        
        # Save Markdown file
        md_path = os.path.join(output_dir, 'sus_uta7_questionnaire.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✓ Markdown saved to: {md_path}")
        return md_path
        
    except Exception as e:
        print(f"Error creating Markdown: {e}")
        return None

def convert_json_to_txt(json_path, output_dir):
    """Convert JSON data to structured plain text format with numbered questions and responses."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        txt_content = "Questions:\n"
        
        # Generate questions section with numbers
        question_num = 1
        for question_key, question_desc in data['questions'].items():
            # Detect question type based on content
            if "scale" in question_desc.lower() or "rating" in question_desc.lower():
                txt_content += f"{question_num}. {question_key}: {question_desc} (Scale/Rating)\n"
            else:
                txt_content += f"{question_num}. {question_key}: {question_desc} (Open-ended)\n"
            question_num += 1
        
        # Add responses section
        txt_content += "\nResponses:\n"
        
        for i, response in enumerate(data['responses']):
            txt_content += f"Respondent {i + 1}:\n"
            
            for answer_key, answer_value in response['answers'].items():
                if answer_value is not None:
                    txt_content += f"- {answer_key}: {answer_value}\n"
                else:
                    txt_content += f"- {answer_key}: (no answer)\n"
            txt_content += "\n"
        
        # Save TXT file
        txt_path = os.path.join(output_dir, 'sus_uta7_questionnaire.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        print(f"✓ TXT saved to: {txt_path}")
        return txt_path
        
    except Exception as e:
        print(f"Error creating TXT: {e}")
        return None

def convert_to_specific_formats(json_path, output_dir, formats_to_generate):
    """Convert JSON to specified formats"""
    print(f"\n=== Converting to requested formats: {', '.join(formats_to_generate)} ===")
    
    formats_created = []
    
    if 'html' in formats_to_generate:
        # Convert to HTML
        html_path = convert_json_to_html(json_path, output_dir)
        if html_path:
            formats_created.append("HTML")
    
    if 'xml' in formats_to_generate:
        # Convert to XML
        xml_path = convert_json_to_xml(json_path, output_dir)
        if xml_path:
            formats_created.append("XML")
    
    if 'markdown' in formats_to_generate:
        # Convert to Markdown
        md_path = convert_json_to_markdown(json_path, output_dir)
        if md_path:
            formats_created.append("Markdown")
    
    if 'txt' in formats_to_generate:
        # Convert to TXT
        txt_path = convert_json_to_txt(json_path, output_dir)
        if txt_path:
            formats_created.append("TXT")
    
    print(f"\n✓ Successfully created {len(formats_created)} format(s): {', '.join(formats_created)}")
    return formats_created

def convert_to_all_formats(json_path, output_dir):
    """Convert JSON to all supported formats"""
    return convert_to_specific_formats(json_path, output_dir, ['html', 'xml', 'markdown', 'txt'])

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Convert SUS-UTA7 survey data to questionnaire formats')
    
    parser.add_argument('--html', action='store_true', help='Generate HTML format')
    parser.add_argument('--json', action='store_true', help='Generate JSON format (always generated as base)')
    parser.add_argument('--xml', action='store_true', help='Generate XML format')
    parser.add_argument('--markdown', action='store_true', help='Generate Markdown format')
    parser.add_argument('--txt', action='store_true', help='Generate raw text format')
    parser.add_argument('--all', action='store_true', help='Generate all formats')
    
    return parser.parse_args()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Convert CSV to JSON (always done as base format)
    json_path = convert_sus_to_json()
    
    # If JSON conversion was successful, convert to requested formats
    if json_path:
        output_dir = os.path.join('preprocessed_data', 'sus-uta7')
        
        # Determine which formats to generate
        if args.all:
            # Generate all formats
            convert_to_all_formats(json_path, output_dir)
        else:
            # Generate specific formats
            formats_to_generate = []
            
            if args.html:
                formats_to_generate.append('html')
            if args.xml:
                formats_to_generate.append('xml')
            if args.markdown:
                formats_to_generate.append('markdown')
            if args.txt:
                formats_to_generate.append('txt')
            
            # If no specific formats are requested, generate all (default behavior)
            if not formats_to_generate:
                formats_to_generate = ['html', 'xml', 'markdown', 'txt']
            
            convert_to_specific_formats(json_path, output_dir, formats_to_generate)
