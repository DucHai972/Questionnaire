import pandas as pd
import json
import os
import re
import argparse
import unicodedata

def clean_text(text):
    """Clean text by removing extra whitespace and normalizing"""
    if text is None:
        return None
    if isinstance(text, str):
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    return text

def examine_csv_structure(csv_path):
    """Examine the CSV file structure to understand the data"""
    try:
        print("=== Examining CSV Structure ===")
        
        # Read first few rows to understand structure
        df_sample = pd.read_csv(csv_path, nrows=5)
        print(f"CSV Shape: {df_sample.shape}")
        print(f"Total Columns: {len(df_sample.columns)}")
        
        print("\nColumn Names (first 10):")
        for i, col in enumerate(df_sample.columns[:10]):
            print(f"  {i+1}. {col}")
        
        if len(df_sample.columns) > 10:
            print(f"  ... and {len(df_sample.columns)-10} more columns")
        
        print("\nSample Data (first 3 rows, first 5 columns):")
        print(df_sample.iloc[:3, :5])
        
        return df_sample.columns.tolist()
        
    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_path}")
        return None
    except Exception as e:
        print(f"Error examining CSV: {e}")
        return None

def convert_csv_to_json():
    """Convert Stack Overflow CSV data to JSON format - 500 responses with minimal NaN values"""
    # Path to the CSV file
    csv_path = os.path.join('data', 'stack-overflow-2022-developer-survey', 'survey_results_public.csv')
    
    # Define the specific questions we want with their descriptions and MCQ options
    selected_questions = {
        "ResponseId": "Respondent's ID number [Open-ended]",
        "MainBranch": "Primary professional identity [MCQ: A. I am a developer by profession B. I am not primarily a developer, but I write code sometimes as part of my work C. I used to be a developer by profession, but no longer am D. I am learning to code E. I code primarily as a hobby F. None of these]",
        "Employment": "Employment status [MCQ-Multi: A. Employed, full-time B. Employed, part-time C. Independent contractor, freelancer, or self-employed D. Not employed, but looking for work E. Not employed, and not looking for work F. Student, full-time G. Student, part-time H. Retired I. Prefer not to say]",
        "EdLevel": "Highest level of education [MCQ: A. Primary/elementary school B. Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.) C. Some college/university study without earning a degree D. Associate degree (A.A., A.S., etc.) E. Bachelor's degree (B.A., B.S., B.Eng., etc.) F. Master's degree (M.A., M.S., M.Eng., MBA, etc.) G. Professional degree (JD, MD, etc.) H. Other doctoral degree (Ph.D., Ed.D., etc.) I. Something else]",
        "YearsCode": "Total years of coding experience [Open-ended]",
        "YearsCodePro": "Years of professional coding experience [Open-ended]",
        "DevType": "Roles in development [Open-ended]",
        "OrgSize": "Size of the organization they work in [Open-ended]",
        "Country": "Country of residence [Open-ended]",
        "CompTotal": "Total compensation [Open-ended]",
        "CompFreq": "Compensation frequency [MCQ: A. Weekly B. Monthly C. Yearly]",
        "LanguageHaveWorkedWith": "Programming languages worked with [Open-ended]",
        "LanguageWantToWorkWith": "Programming languages they want to use [Open-ended]",
        "ToolsTechHaveWorkedWith": "Developer tools used [Open-ended]",
        "VersionControlSystem": "Version control systems used [MCQ: A. Git B. Mercurial C. SVN D. I don't use one]"
    }
    
    # Create MCQ mappings for converting full text answers to letter codes
    mcq_mappings = {
        "MainBranch": {
            "I am a developer by profession": "A",
            "I am not primarily a developer, but I write code sometimes as part of my work": "B", 
            "I used to be a developer by profession, but no longer am": "C",
            "I am learning to code": "D",
            "I code primarily as a hobby": "E",
            "None of these": "F"
        },
        "Employment": {
            "Employed, full-time": "A",
            "Employed, part-time": "B", 
            "Independent contractor, freelancer, or self-employed": "C",
            "Not employed, but looking for work": "D",
            "Not employed, and not looking for work": "E",
            "Student, full-time": "F",
            "Student, part-time": "G",
            "Retired": "H",
            "Prefer not to say": "I"
        },
        "EdLevel": {
            "Primary/elementary school": "A",
            "Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.)": "B",
            "Some college/university study without earning a degree": "C", 
            "Associate degree (A.A., A.S., etc.)": "D",
            "Bachelor's degree (B.A., B.S., B.Eng., etc.)": "E",
            "Bachelor's degree (B.A., B.S., B.Eng., etc.)": "E",  # Handle Unicode apostrophe
            "Bachelor's degree (B.A., B.S., B.Eng., etc.)": "E",  # Handle another Unicode apostrophe variation
            "Master's degree (M.A., M.S., M.Eng., MBA, etc.)": "F",
            "Master's degree (M.A., M.S., M.Eng., MBA, etc.)": "F",  # Handle Unicode apostrophe
            "Master's degree (M.A., M.S., M.Eng., MBA, etc.)": "F",  # Handle another Unicode apostrophe variation
            "Professional degree (JD, MD, etc.)": "G",
            "Other doctoral degree (Ph.D., Ed.D., etc.)": "H",
            "Something else": "I"
        },
        "CompFreq": {
            "Weekly": "A",
            "Monthly": "B",
            "Yearly": "C"
        },
        "VersionControlSystem": {
            "Git": "A",
            "Mercurial": "B", 
            "SVN": "C",
            "I don't use one": "D"
        }
    }
    
    def convert_mcq_answer(question_code, answer_value):
        """Convert MCQ answer from full text to letter code"""
        if question_code not in mcq_mappings or answer_value is None:
            return answer_value
            
        mapping = mcq_mappings[question_code]
        
        # Normalize text to handle character encoding differences
        def normalize_text(text):
            # Replace various apostrophe and quote characters with standard apostrophe
            text = text.replace("'", "'").replace("'", "'").replace("′", "'")
            text = text.replace(""", '"').replace(""", '"')  # Handle quote marks
            text = text.replace("–", "-").replace("—", "-")  # Handle dashes
            # Handle any remaining Unicode quotation marks
            # Normalize to decomposed form and then back to composed
            text = unicodedata.normalize('NFKD', text)
            text = unicodedata.normalize('NFKC', text)
            return text
        
        # Handle multi-select questions (like Employment) - semicolon separated
        if ';' in str(answer_value):
            answers = [ans.strip() for ans in str(answer_value).split(';')]
            letter_codes = []
            for ans in answers:
                normalized_ans = normalize_text(ans)
                # Try both original and normalized versions
                if ans in mapping:
                    letter_codes.append(mapping[ans])
                elif normalized_ans in mapping:
                    letter_codes.append(mapping[normalized_ans])
                else:
                    letter_codes.append(ans)  # Keep original if not found
            return letter_codes
        else:
            # Single answer
            normalized_value = normalize_text(answer_value)
            # Try both original and normalized versions
            if answer_value in mapping:
                return mapping[answer_value]
            elif normalized_value in mapping:
                return mapping[normalized_value]
            else:
                return answer_value
    
    try:
        print("Reading Stack Overflow CSV file...")
        
        # First examine the structure
        columns = examine_csv_structure(csv_path)
        if columns is None:
            return None
        
        # Read the full CSV file
        print("\nReading full CSV file...")
        df = pd.read_csv(csv_path)
        print(f"Successfully loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Check which selected questions exist in the data
        available_questions = {}
        missing_questions = []
        
        for question_code, description in selected_questions.items():
            if question_code in df.columns:
                available_questions[question_code] = description
            else:
                missing_questions.append(question_code)
        
        print(f"Found {len(available_questions)} out of {len(selected_questions)} selected questions")
        if missing_questions:
            print(f"Missing questions: {missing_questions}")
        
        # Filter to only selected columns that exist
        df_selected = df[list(available_questions.keys())]
        
        # Filter responses with minimal NaN values (only for selected columns)
        print("Filtering responses with minimal NaN values...")
        
        # Calculate NaN percentage for each row (only for selected columns)
        df_selected['nan_percentage'] = df_selected.isnull().sum(axis=1) / len(available_questions) * 100
        
        # Sort by NaN percentage (ascending - least NaN first)
        df_sorted = df_selected.sort_values('nan_percentage')  # type: ignore
        
        # Take first 500 responses with minimal NaN values
        df_filtered = df_sorted.head(500).drop('nan_percentage', axis=1)
        
        print(f"Selected 500 responses with minimal NaN values")
        print(f"Average NaN percentage in selected data: {df_sorted.head(500)['nan_percentage'].mean():.1f}%")
        
        # Create JSON structure according to the specified format
        data = {
            "questions": [],
            "responses": []
        }
        
        # Add questions as strings with format "QuestionCode: Description"
        print("Processing questions...")
        for question_code in df_filtered.columns:
            if question_code in available_questions:
                question_string = f"{question_code}: {available_questions[question_code]}"
                data["questions"].append(question_string)
        
        # Process responses
        print("Processing 500 selected responses...")
        for idx, (_, row) in enumerate(df_filtered.iterrows()):
            response = {
                "answers": {}
            }
            
            # Process each column/question
            for column in df_filtered.columns:
                value = row[column]
                
                # Clean and process the value
                if value is None or (isinstance(value, (int, float)) and pd.isna(value)):
                    response["answers"][column] = None
                else:
                    # Convert to appropriate type
                    if isinstance(value, (int, float)):
                        response["answers"][column] = value
                    else:
                        cleaned_value = clean_text(str(value))
                        if cleaned_value:
                            # Apply MCQ conversion if applicable
                            converted_value = convert_mcq_answer(column, cleaned_value)
                            response["answers"][column] = converted_value
                        else:
                            response["answers"][column] = None
            
            data["responses"].append(response)
            
            # Progress indicator
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1} responses...")
        
        # Create output directory
        output_dir = os.path.join('preprocessed_data', 'stack-overflow-2022-developer-survey')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to JSON file
        json_path = os.path.join(output_dir, 'survey_results_sample.json')
        print(f"\nSaving JSON to: {json_path}")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ JSON saved to: {json_path}")
        print(f"✓ Total responses: {len(data['responses'])}")
        print(f"✓ Total questions: {len(data['questions'])}")
        
        # Show file size
        file_size = os.path.getsize(json_path) / (1024 * 1024)  # MB
        print(f"✓ File size: {file_size:.1f} MB")
        
        return json_path
        
    except FileNotFoundError:
        print(f"Error: File not found at {csv_path}")
        print("Please make sure the file exists in the correct location.")
        return None
    except Exception as e:
        print(f"Error processing the file: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def convert_json_to_html(json_path, output_dir):
    """Convert JSON data to HTML format matching the specified structure"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        def format_answer_value(value):
            """Format answer value for display"""
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return str(value) if value is not None else "(missing)"
        
        # Start HTML content
        html_content = "<h1>Questions</h1>\n<ul>\n"
        
        # Add questions section - extract question code and description from the format "QuestionCode: Description"
        for question in data['questions']:
            if ':' in question:
                question_code, description = question.split(':', 1)
                question_code = question_code.strip()
                description = description.strip()
                html_content += f"  <li><strong>{question_code}:</strong> {description}</li>\n"
            else:
                # Fallback if format is different
                html_content += f"  <li><strong>{question}:</strong></li>\n"
        
        html_content += "</ul>\n\n"
        
        # Add responses section
        html_content += "<h1>Responses</h1>\n"
        
        for i, response in enumerate(data['responses']):
            html_content += f"<h2>Respondent {i + 1}</h2>\n"
            html_content += "<ul>\n"
            
            # Get all question keys (should match the order of questions)
            if data['responses']:
                all_question_keys = list(response['answers'].keys())
                
                for question_key in all_question_keys:
                    answer_value = response['answers'].get(question_key)
                    formatted_value = format_answer_value(answer_value)
                    html_content += f"  <li><strong>{question_key}:</strong> {formatted_value}</li>\n"
            
            html_content += "</ul>\n\n"
        
        # Save HTML file
        html_path = os.path.join(output_dir, 'survey_results_sample.html')
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
            opt_match = re.search(r'MCQ(?:-Multi)?: (.+?)\]', text)
            if not opt_match:
                return []
            opts = opt_match.group(1)
            # Split by letter markers and clean up
            options = []
            parts = re.split(r'\s*([A-Z])\.\s*', opts)
            for i in range(1, len(parts)-1, 2):
                letter = parts[i]
                value = parts[i+1].strip()
                if value.endswith(' '):
                    value = value[:-1]
                options.append((letter, value))
            return options
        
        # Process questions
        for question in data['questions']:
            # Parse question string
            parts = question.split(':', 1)
            if len(parts) != 2:
                continue
                
            question_key = parts[0].strip()
            if question_key == "ResponseId":
                continue  # Skip the response ID
                
            # Generate question ID
            q_id = to_camel_case(question_key)
            
            # Extract question type and text
            question_desc = parts[1].strip()
            type_match = re.search(r'\[(.*?)\]', question_desc)
            if type_match:
                type_str = type_match.group(1)
                q_text = question_desc.split('[')[0].strip()
            else:
                type_str = "Open-ended"
                q_text = question_desc
            
            if "MCQ" in type_str:
                # MCQ question with options
                xml_content += f'    <question id="{q_id}" type="mcq">{q_text}\n'
                options = extract_mcq_options(question_desc)
                for letter, val in options:
                    xml_content += f'      <option value="{letter}">{val.strip()}</option>\n'
                xml_content += '    </question>\n'
            else:
                # Open-ended question
                xml_content += f'    <question id="{q_id}" type="open-ended">{q_text}</question>\n'
        
        xml_content += '  </questions>\n'
        
        # Add Responses section
        xml_content += '  <responses>\n'
        
        for i, response in enumerate(data['responses']):
            xml_content += f'    <respondent id="{i+1}">\n'
            
            for answer_key, answer_value in response['answers'].items():
                if answer_key == "ResponseId":
                    continue  # Skip the response ID
                    
                # Convert key to camelCase for XML
                xml_key = to_camel_case(answer_key)
                
                if isinstance(answer_value, list):
                    # Handle multi-select answers
                    xml_content += f'      <{xml_key}>'
                    xml_content += ','.join(str(v) for v in answer_value)
                    xml_content += f'</{xml_key}>\n'
                else:
                    # Handle single answers
                    xml_content += f'      <{xml_key}>{answer_value}</{xml_key}>\n'
            
            xml_content += '    </respondent>\n'
        
        xml_content += '  </responses>\n'
        xml_content += '</questionnaire>\n'
        
        # Save XML file
        xml_path = os.path.join(output_dir, 'stack_overflow_questionnaire.xml')
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
        
        def format_answer_value(value):
            """Format answer value for display"""
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return str(value) if value is not None else "*No answer*"
        
        # Add questions
        md_content = "## Questions\n\n"
        for i, question in enumerate(data['questions']):
            md_content += f"- **Question {i+1}:** {question}\n"
        md_content += "\n"
        
        # Add responses
        md_content += "## Responses\n\n"
        for i, response in enumerate(data['responses']):
            md_content += f"### Respondent {i + 1}\n\n"
            
            for answer_key, answer_value in response['answers'].items():
                formatted_value = format_answer_value(answer_value)
                md_content += f"- **{answer_key}:** {formatted_value}\n"
            md_content += "\n"
        
        # Save Markdown file
        md_path = os.path.join(output_dir, 'survey_results_sample.md')
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
        
        def format_answer_value(value):
            """Format answer value for display"""
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return str(value) if value is not None else "(no answer)"
        
        def parse_question_string(question_string):
            """Parse question string to extract code and description."""
            if ':' in question_string:
                parts = question_string.split(':', 1)
                code = parts[0].strip()
                desc = parts[1].strip()
                
                # Detect question type from description
                if "[MCQ:" in desc or "[MCQ-Multi:" in desc:
                    return code, desc, "mcq"
                elif "[Open-ended]" in desc:
                    return code, desc, "open-ended"
                else:
                    return code, desc, "open-ended"
            else:
                return question_string, "", "unknown"
        
        txt_content = "Questions:\n"
        
        # Generate questions section with numbers
        for i, question in enumerate(data['questions']):
            question_num = i + 1
            code, desc, qtype = parse_question_string(question)
            
            if qtype == "mcq":
                txt_content += f"{question_num}. {code}: {desc} (MCQ)\n"
            else:
                txt_content += f"{question_num}. {code}: {desc} (Open-ended)\n"
        
        # Add responses section
        txt_content += "\nResponses:\n"
        
        for i, response in enumerate(data['responses']):
            txt_content += f"Respondent {i + 1}:\n"
            
            for answer_key, answer_value in response['answers'].items():
                formatted_value = format_answer_value(answer_value)
                txt_content += f"- {answer_key}: {formatted_value}\n"
            txt_content += "\n"
        
        # Save TXT file
        txt_path = os.path.join(output_dir, 'survey_results_sample.txt')
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
    parser = argparse.ArgumentParser(description='Convert Stack Overflow survey data to questionnaire formats')
    
    parser.add_argument('--html', action='store_true', help='Generate HTML format')
    parser.add_argument('--json', action='store_true', help='Generate JSON format (always generated as base)')
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
        formats_to_generate = ['html', 'xml', 'markdown', 'txt']
    else:
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
        formats_to_generate = ['html', 'xml', 'markdown', 'txt']
    
    # Convert CSV to JSON (always done as base format)
    json_path = convert_csv_to_json()
    
    # If JSON conversion was successful, convert to requested formats
    if json_path:
        output_dir = os.path.join('preprocessed_data', 'stack-overflow-2022-developer-survey')
        convert_to_specific_formats(json_path, output_dir, formats_to_generate)
