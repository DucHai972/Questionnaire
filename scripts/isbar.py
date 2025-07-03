import json
import os
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

def create_questions_schema():
    """Create the questions schema with detailed descriptions and rubrics."""
    return {
        "date": "What is the date of the session? [Open-ended]",
        "sessionName": "What is the name of the session? [Open-ended]",
        "identification": "Identification of self, role, and patient. [Rubric: 0 = Requires direct prompting, 1 = Introduces themselves but only after a hint, 2 = Introduces themselves but information is incomplete, 3 = Introduces themselves and information is complete]",
        "situation": "Identifies the main problem(s). [Rubric: 0 = Unable to identify the main problem(s), 1 = Identifies the main problem(s) after extended prompting, 2 = Identifies the main problem(s) with fewer prompts needed, 3 = Identifies and prioritizes the main problem(s) unprompted]",
        "background (history)": "Gives appropriate history. [Rubric: 0 = History is unstructured or non-relevant, 1 = Relevant history but frequent clarification needed, 2 = Relevant history with few further questions needed, 3 = Comprehensive focused history]",
        "background (examination)": "Gives appropriate examination/observations. [Rubric: 0 = Observations are omitted or irrelevant, 1 = Observations reported but frequent clarification needed, 2 = Observations reported with few further questions needed, 3 = Comprehensive focused examination/observations]",
        "assessment": "Makes logical assessment (correlates problem, history, exam, context). [Rubric: 0 = No logical assessment, 1 = Assessment only after extended questioning, 2 = Assessment after minimal questioning, 3 = Comprehensive logical assessment without questioning]",
        "recommendation (clear recommendation)": "Makes a clear recommendation. [Rubric: 0 = No recommendation, 1 = Clear recommendation only after extended questioning, 2 = Clear recommendation after minimal questioning, 3 = Clear comprehensive recommendation without questioning]",
        "recommendation (global rating scale)": "Global Rating Scale (GRS) - How confident am I that I received an accurate picture of the patient? [Rubric: 0 = Not at all confident, 1 = Confident but required extended questioning, 2 = Confident but required some further questioning, 3 = Confident and required little or no questioning]",
        "comments": "Comments on the session. [Open-ended]"
    }

def process_isbar_file(file_path):
    """Process a single ISBAR JSON file and return the answers object."""
    
    # Read the original file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract responses from the original format
    answers = {
        "date": data["sessionInfo"]["date"],
        "sessionName": data["sessionInfo"]["sessionName"],
        "identification": data["scores"]["identification"],
        "situation": data["scores"]["situation"],
        "background (history)": data["scores"]["background (history)"],
        # Handle the typo in the original data - could be "backrgound" or "background"
        "background (examination)": data["scores"].get("background (examination)", 
                                                        data["scores"].get("backrgound (examination)")),
        "assessment": data["scores"]["assessment"],
        "recommendation (clear recommendation)": data["scores"]["recommendation (clear recommendation)"],
        "recommendation (global rating scale)": data["scores"]["recommendation (global rating scale)"],
        "comments": data["comments"]
    }
    
    return answers

def load_combined_data():
    """Load the combined ISBAR JSON data."""
    json_path = Path("preprocessed_data/isbar/isbar_combined.json")
    
    if not json_path.exists():
        print(f"Combined JSON file not found: {json_path}")
        print("Please run the script without flags first to generate the combined JSON.")
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_value(value):
    """Format a value for display, handling missing values and arrays."""
    if value is None or value == "":
        return "N/A"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)

def generate_html(data, output_path):
    """Generate HTML format."""
    questions = data["questions"]
    responses = data["responses"]
    
    html_content = ""
    
    # Add Questions section
    html_content += "<h1>Questions</h1>\n<ul>\n"
    for key, description in questions.items():
        html_content += f'  <li><strong>{key}:</strong> {description}</li>\n'
    html_content += "</ul>\n\n"
    
    # Add Responses section
    html_content += "<h1>Responses</h1>\n"
    for i, response in enumerate(responses, 1):
        html_content += f"<h2>Session {i}</h2>\n<ul>\n"
        for key, value in response.items():
            formatted_value = format_value(value)
            html_content += f'  <li><strong>{key}:</strong> {formatted_value}</li>\n'
        html_content += "</ul>\n\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML format saved to: {output_path}")

def generate_xml(data, output_path):
    """Generate XML format."""
    root = ET.Element("isbar_data")
    
    # Add Questions section
    questions_elem = ET.SubElement(root, "questions")
    for key, description in data["questions"].items():
        question_elem = ET.SubElement(questions_elem, "question")
        question_elem.set("key", key)
        question_elem.text = description
    
    # Add Responses section
    responses_elem = ET.SubElement(root, "responses")
    for i, response in enumerate(data["responses"], 1):
        session_elem = ET.SubElement(responses_elem, "session")
        session_elem.set("id", str(i))
        
        for key, value in response.items():
            field_elem = ET.SubElement(session_elem, "field")
            field_elem.set("name", key)
            field_elem.text = format_value(value)
    
    # Pretty print XML
    from xml.dom import minidom
    rough_string = ET.tostring(root, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    
    print(f"XML format saved to: {output_path}")

def generate_markdown(data, output_path):
    """Generate Markdown format."""
    questions = data["questions"]
    responses = data["responses"]
    
    md_content = "# ISBAR Assessment Data\n\n"
    
    # Add Questions section
    md_content += "## Questions\n\n"
    for key, description in questions.items():
        md_content += f"- **{key}:** {description}\n"
    md_content += "\n"
    
    # Add Responses section
    md_content += "## Responses\n\n"
    for i, response in enumerate(responses, 1):
        md_content += f"### Session {i}\n\n"
        for key, value in response.items():
            formatted_value = format_value(value)
            if key == "comments" and formatted_value != "N/A":
                # Handle multi-line comments in markdown
                formatted_value = formatted_value.replace('\n', '  \n')
            md_content += f"- **{key}:** {formatted_value}\n"
        md_content += "\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Markdown format saved to: {output_path}")

def generate_txt(data, output_path):
    """Generate plain text format."""
    questions = data["questions"]
    responses = data["responses"]
    
    txt_content = "ISBAR ASSESSMENT DATA\n"
    txt_content += "=" * 50 + "\n\n"
    
    # Add Questions section
    txt_content += "QUESTIONS\n"
    txt_content += "-" * 20 + "\n\n"
    for key, description in questions.items():
        txt_content += f"{key}: {description}\n\n"
    
    # Add Responses section
    txt_content += "\nRESPONSES\n"
    txt_content += "-" * 20 + "\n\n"
    for i, response in enumerate(responses, 1):
        txt_content += f"Session {i}\n"
        txt_content += "." * 15 + "\n"
        for key, value in response.items():
            formatted_value = format_value(value)
            txt_content += f"{key}: {formatted_value}\n"
        txt_content += "\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    
    print(f"TXT format saved to: {output_path}")

def combine_isbar_files():
    """Combine all ISBAR files into one JSON (original functionality)."""
    
    # Define paths
    input_dir = Path("data/isbar")
    output_dir = Path("preprocessed_data/isbar")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all JSON files in the input directory
    json_files = list(input_dir.glob("*.json"))
    
    if not json_files:
        print("No JSON files found in data/isbar directory")
        return
    
    print(f"Found {len(json_files)} JSON files to process")
    
    # Create the questions schema
    questions = create_questions_schema()
    
    # Process all files and collect answers
    all_answers = []
    
    for json_file in json_files:
        try:
            answers = process_isbar_file(json_file)
            all_answers.append(answers)
            print(f"Processed: {json_file.name}")
            
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
    
    # Create the combined structure
    combined_data = {
        "questions": questions,
        "responses": all_answers
    }
    
    # Write the combined file
    output_file = output_dir / "isbar_combined.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nCombined {len(all_answers)} sessions into: {output_file}")
    print(f"Total responses: {len(all_answers)}")

def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(description="ISBAR data processor and format converter")
    parser.add_argument("--json", action="store_true", help="Generate JSON format (combine original files)")
    parser.add_argument("--html", action="store_true", help="Generate HTML format")
    parser.add_argument("--xml", action="store_true", help="Generate XML format")
    parser.add_argument("--markdown", action="store_true", help="Generate Markdown format")
    parser.add_argument("--txt", action="store_true", help="Generate TXT format")
    
    args = parser.parse_args()
    
    # If no flags provided, default to JSON generation (original behavior)
    if not any([args.json, args.html, args.xml, args.markdown, args.txt]):
        args.json = True
    
    output_dir = Path("preprocessed_data/isbar")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Handle JSON generation (original functionality)
    if args.json:
        combine_isbar_files()
    
    # Handle other format conversions
    if any([args.html, args.xml, args.markdown, args.txt]):
        data = load_combined_data()
        if data is None:
            return
        
        if args.html:
            generate_html(data, output_dir / "isbar_combined.html")
        
        if args.xml:
            generate_xml(data, output_dir / "isbar_combined.xml")
        
        if args.markdown:
            generate_markdown(data, output_dir / "isbar_combined.md")
        
        if args.txt:
            generate_txt(data, output_dir / "isbar_combined.txt")

if __name__ == "__main__":
    main()
