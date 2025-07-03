import pandas as pd
import json
import os
import re
import argparse

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

def get_question_metadata():
    """Define the question metadata structure"""
    return {
        "Year of birth": "What is your date of birth? [Open-ended]",
        "Gender": "What is your gender? [MCQ: 1. Male 2. Female]",
        "Socio-economic status": "What is the socio-economic status of your home? [Likert 1–6: 1 = Very low, 6 = Very high]",
        "Ethnic identity": "According to your culture, people, or physical features, you are or are recognized as: [MCQ: 1. Indigenous 2. Gypsy 3. Raizal from San Andres, Providencia and Santa Catalina Archipelago 4. Palenquero from San Basilio 5. Black, mulatto (Afro-descendant), Afro-Colombian 6. None of the above]",
        "Parental Education": {
            "base_question": "How many years of education did your parents receive? [Open-ended]",
            "sub_questions": {
                "Father": "Father?",
                "Mother": "Mother?"
            }
        },
        "Life satisfaction": "In general, how satisfied are you with all aspects of your life? [Likert 0–10: 0 = Not satisfied, 10 = Totally satisfied]",
        "Happiness": "How happy did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Laughter": "How much did you laugh yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Learning": "Did you learn new or exciting things yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Enjoyment": "How much did you enjoy the activities you did yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Worry": "How worried did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Depression": "How depressed did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Anger": "How angry did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Stress": "How much stress did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Loneliness": "How lonely or unsupported did you feel yesterday? [Likert 0–10: 0 = At no time, 10 = All the time]",
        "Emotional Regulation Frequency": {
            "base_question": "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 4, where 0 is never, 1 is 'almost never', 2 is 'sometimes', 3 is 'fairly often', and 4 is 'very often', how often you experienced the following feelings during the last month: [Likert 0–4]",
            "sub_questions": {
                "Upset by Unexpected Events": "how often have you been upset because of something that happened unexpectedly?",
                "Unable to Control Important Things": "how often have you felt that you were unable to control the important things in your life?",
                "Nervous and Stressed": "how often have you felt nervous and stressed?",
                "Lacked Confidence Handling Problems": "how often have you felt confident about your ability to handle your personal problems?",
                "Things Going Your Way": "how often have you felt that things were going your way?",
                "Unable to Cope": "how often have you found that you could not cope with all the things that you had to do?",
                "Irritated by Life": "how often have you been able to control irritations in your life?",
                "On Top of Things": "how often have you felt that you were on top of things?",
                "Angered by Uncontrollable Events": "how often have you been angered because of things that happened that were outside of your control?",
                "Felt Overwhelmed": "how often have you felt difficulties were piling up so high that you could not overcome them?"
            }
        },
        "Anxiety Symptoms Frequency": {
            "base_question": "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems? [Likert 0–3]",
            "sub_questions": {
                "Feeling Nervous or On Edge": "Feeling nervous, anxious, or on edge",
                "Uncontrollable Worrying": "Not being able to stop or control worrying",
                "Excessive Worry": "Worrying too much about different things",
                "Trouble Relaxing": "Trouble relaxing",
                "Restlessness": "Being so restless that it is hard to sit still",
                "Irritability": "Becoming easily annoyed or irritable",
                "Fear Something Awful Might Happen": "Feeling afraid, as if something awful might happen"
            }
        },
        "Depressive Symptoms Frequency": {
            "base_question": "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems?",
            "sub_questions": {
                "Anhedonia": "Little interest or pleasure in doing things",
                "Depressed Mood": "Feeling down, depressed, or hopeless",
                "Sleep Problems": "Trouble falling or staying asleep, or sleeping too much",
                "Fatigue": "Feeling tired or having little energy",
                "Appetite Changes": "Poor appetite or overeating",
                "Feelings of Worthlessness": "Feeling bad about yourself or that you are a failure or have let yourself or your family down",
                "Concentration Difficulties": "Trouble concentrating on things, such as reading the newspaper or watching television",
                "Psychomotor Changes": "Moving or speaking so slowly that other people could have noticed. Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual",
                "Suicidal Thoughts": "Thoughts that you would be better off dead, or of hurting yourself"
            }
        }
    }

def create_column_mapping():
    """Create mapping from Excel columns to JSON structure"""
    # This mapping will need to be adjusted based on the actual Excel column names
    # You'll need to examine the Excel file to match column names to these keys
    return {
        # Simple mappings - adjust these based on actual Excel column names
        "Year of birth": "Year of birth",
        "Gender": "Gender", 
        "Socio-economic status": "Socio-economic status",
        "Ethnic identity": "Ethnic identity",
        "Life satisfaction": "Life satisfaction",
        "Happiness": "Happiness",
        "Laughter": "Laughter", 
        "Learning": "Learning",
        "Enjoyment": "Enjoyment",
        "Worry": "Worry",
        "Depression": "Depression",
        "Anger": "Anger",
        "Stress": "Stress",
        "Loneliness": "Loneliness",
        
        # Parental Education mappings
        "Father education": ("Parental Education", "Father"),
        "Mother education": ("Parental Education", "Mother"),
        
        # Emotional Regulation Frequency mappings
        "Upset by unexpected": ("Emotional Regulation Frequency", "Upset by Unexpected Events"),
        "Unable to control important": ("Emotional Regulation Frequency", "Unable to Control Important Things"),
        "Nervous and stressed": ("Emotional Regulation Frequency", "Nervous and Stressed"),
        "Lacked confidence": ("Emotional Regulation Frequency", "Lacked Confidence Handling Problems"),
        "Things going your way": ("Emotional Regulation Frequency", "Things Going Your Way"),
        "Unable to cope": ("Emotional Regulation Frequency", "Unable to Cope"),
        "Irritated by life": ("Emotional Regulation Frequency", "Irritated by Life"),
        "On top of things": ("Emotional Regulation Frequency", "On Top of Things"),
        "Angered by uncontrollable": ("Emotional Regulation Frequency", "Angered by Uncontrollable Events"),
        "Felt overwhelmed": ("Emotional Regulation Frequency", "Felt Overwhelmed"),
        
        # Anxiety Symptoms mappings
        "Feeling nervous": ("Anxiety Symptoms Frequency", "Feeling Nervous or On Edge"),
        "Uncontrollable worrying": ("Anxiety Symptoms Frequency", "Uncontrollable Worrying"),
        "Excessive worry": ("Anxiety Symptoms Frequency", "Excessive Worry"),
        "Trouble relaxing": ("Anxiety Symptoms Frequency", "Trouble Relaxing"),
        "Restlessness": ("Anxiety Symptoms Frequency", "Restlessness"),
        "Irritability": ("Anxiety Symptoms Frequency", "Irritability"),
        "Fear something awful": ("Anxiety Symptoms Frequency", "Fear Something Awful Might Happen"),
        
        # Depressive Symptoms mappings
        "Anhedonia": ("Depressive Symptoms Frequency", "Anhedonia"),
        "Depressed mood": ("Depressive Symptoms Frequency", "Depressed Mood"),
        "Sleep problems": ("Depressive Symptoms Frequency", "Sleep Problems"),
        "Fatigue": ("Depressive Symptoms Frequency", "Fatigue"),
        "Appetite changes": ("Depressive Symptoms Frequency", "Appetite Changes"),
        "Feelings worthlessness": ("Depressive Symptoms Frequency", "Feelings of Worthlessness"),
        "Concentration difficulties": ("Depressive Symptoms Frequency", "Concentration Difficulties"),
        "Psychomotor changes": ("Depressive Symptoms Frequency", "Psychomotor Changes"),
        "Suicidal thoughts": ("Depressive Symptoms Frequency", "Suicidal Thoughts")
    }

def find_best_column_match(excel_columns, target_key):
    """Find the best matching Excel column for a target key"""
    target_key_lower = target_key.lower()
    best_match = None
    best_score = 0
    
    for col in excel_columns:
        col_lower = str(col).lower()
        
        # Check for exact match
        if target_key_lower in col_lower or col_lower in target_key_lower:
            # Simple word matching score
            target_words = set(target_key_lower.split())
            col_words = set(col_lower.split())
            common_words = target_words.intersection(col_words)
            score = len(common_words) / max(len(target_words), len(col_words))
            
            if score > best_score:
                best_score = score
                best_match = col
    
    return best_match if best_score > 0.3 else None

def auto_map_columns(excel_columns):
    """Automatically map Excel columns to JSON structure based on content similarity"""
    mapping = {}
    
    # Direct mappings based on actual Excel column text
    direct_mappings = {
        "1. Year of birth:": "Year of birth",
        "2. Gender": "Gender",
        "3. What is the socio-economic status of your home?": "Socio-economic status",
        "4. According to your culture, people, or physical features, you are or are recognized as:": "Ethnic identity",
        "5.1 How many years of education did your parents receive? Father": ("Parental Education", "Father"),
        "5.2 How many years of education did your parents receive? Mother": ("Parental Education", "Mother"),
        "6. In general, how satisfied are you with all aspects of your life?": "Life satisfaction",
        "7. How happy did you feel yesterday?": "Happiness",
        "8. How much did you laugh yesterday?": "Laughter",
        "9. Did you learn new or exciting  things yesterday?": "Learning",
        "10. How much did you enjoy the activities you did yesterday?": "Enjoyment",
        "11. How worried did you feel yesterday?": "Worry",
        "12. How depressed did you feel yesterday?": "Depression",
        "13. How angry did you feel yesterday?": "Anger",
        "14. How much stress did you feel yesterday?": "Stress",
        "15. How lonely or unsupported did you feel yesterday?": "Loneliness"
    }
    
    # Simple question mappings for partial matches
    simple_mappings = {
        "year": "Year of birth",
        "birth": "Year of birth", 
        "gender": "Gender",
        "socio": "Socio-economic status",
        "economic": "Socio-economic status",
        "ethnic": "Ethnic identity",
        "identity": "Ethnic identity",
        "culture": "Ethnic identity",
        "recognized": "Ethnic identity",
        "satisfaction": "Life satisfaction",
        "satisfied": "Life satisfaction",
        "happy": "Happiness",
        "laugh": "Laughter",
        "learn": "Learning",
        "exciting": "Learning",
        "enjoy": "Enjoyment",
        "activities": "Enjoyment",
        "worried": "Worry",
        "worry": "Worry",
        "depress": "Depression",
        "anger": "Anger",
        "angry": "Anger",
        "stress": "Stress",
        "lonel": "Loneliness",
        "lonely": "Loneliness",
        "unsupported": "Loneliness"
    }
    
    # Group mappings
    group_mappings = {
        # Parental Education - already handled in direct_mappings
        "father": ("Parental Education", "Father"),
        "mother": ("Parental Education", "Mother"),
        "education" + "father": ("Parental Education", "Father"),
        "education" + "mother": ("Parental Education", "Mother"),
        
        # Emotional Regulation Frequency (PSS scale questions)
        "upset" + "unexpected": ("Emotional Regulation Frequency", "Upset by Unexpected Events"),
        "unable" + "control": ("Emotional Regulation Frequency", "Unable to Control Important Things"), 
        "nervous" + "stressed": ("Emotional Regulation Frequency", "Nervous and Stressed"),
        "confident" + "ability": ("Emotional Regulation Frequency", "Lacked Confidence Handling Problems"),
        "things" + "going": ("Emotional Regulation Frequency", "Things Going Your Way"),
        "could not cope": ("Emotional Regulation Frequency", "Unable to Cope"),
        "control irritations": ("Emotional Regulation Frequency", "Irritated by Life"),
        "on top": ("Emotional Regulation Frequency", "On Top of Things"),
        "angered" + "outside": ("Emotional Regulation Frequency", "Angered by Uncontrollable Events"),
        "difficulties" + "piling": ("Emotional Regulation Frequency", "Felt Overwhelmed"),
        
        # GAD-7 Anxiety Symptoms
        "nervous" + "anxious" + "edge": ("Anxiety Symptoms Frequency", "Feeling Nervous or On Edge"),
        "stop" + "control" + "worrying": ("Anxiety Symptoms Frequency", "Uncontrollable Worrying"),
        "worrying too much": ("Anxiety Symptoms Frequency", "Excessive Worry"),
        "trouble relaxing": ("Anxiety Symptoms Frequency", "Trouble Relaxing"),
        "restless" + "hard to sit": ("Anxiety Symptoms Frequency", "Restlessness"),
        "easily annoyed": ("Anxiety Symptoms Frequency", "Irritability"),
        "afraid" + "awful": ("Anxiety Symptoms Frequency", "Fear Something Awful Might Happen"),
        
        # PHQ-9 Depressive Symptoms  
        "little interest" + "pleasure": ("Depressive Symptoms Frequency", "Anhedonia"),
        "feeling down" + "depressed" + "hopeless": ("Depressive Symptoms Frequency", "Depressed Mood"),
        "trouble falling" + "staying asleep" + "sleeping too much": ("Depressive Symptoms Frequency", "Sleep Problems"),
        "feeling tired" + "little energy": ("Depressive Symptoms Frequency", "Fatigue"),
        "poor appetite" + "overeating": ("Depressive Symptoms Frequency", "Appetite Changes"),
        "feeling bad about yourself" + "failure": ("Depressive Symptoms Frequency", "Feelings of Worthlessness"),
        "trouble concentrating": ("Depressive Symptoms Frequency", "Concentration Difficulties"),
        "moving" + "speaking slowly" + "fidgety" + "restless": ("Depressive Symptoms Frequency", "Psychomotor Changes"),
        "better off dead" + "hurting yourself": ("Depressive Symptoms Frequency", "Suicidal Thoughts"),
        
        # Keyword-based fallbacks
        "upset": ("Emotional Regulation Frequency", "Upset by Unexpected Events"),
        "control": ("Emotional Regulation Frequency", "Unable to Control Important Things"),
        "confident": ("Emotional Regulation Frequency", "Lacked Confidence Handling Problems"),
        "cope": ("Emotional Regulation Frequency", "Unable to Cope"),
        "irritat": ("Emotional Regulation Frequency", "Irritated by Life"),
        "overwhelm": ("Emotional Regulation Frequency", "Felt Overwhelmed"),
        "edge": ("Anxiety Symptoms Frequency", "Feeling Nervous or On Edge"),
        "relax": ("Anxiety Symptoms Frequency", "Trouble Relaxing"),
        "restless": ("Anxiety Symptoms Frequency", "Restlessness"),
        "annoyed": ("Anxiety Symptoms Frequency", "Irritability"),
        "awful": ("Anxiety Symptoms Frequency", "Fear Something Awful Might Happen"),
        "interest": ("Depressive Symptoms Frequency", "Anhedonia"),
        "hopeless": ("Depressive Symptoms Frequency", "Depressed Mood"),
        "sleep": ("Depressive Symptoms Frequency", "Sleep Problems"),
        "tired": ("Depressive Symptoms Frequency", "Fatigue"),
        "appetite": ("Depressive Symptoms Frequency", "Appetite Changes"),
        "failure": ("Depressive Symptoms Frequency", "Feelings of Worthlessness"),
        "concentrat": ("Depressive Symptoms Frequency", "Concentration Difficulties"),
        "slowly": ("Depressive Symptoms Frequency", "Psychomotor Changes"),
        "dead": ("Depressive Symptoms Frequency", "Suicidal Thoughts")
    }
    
    for col in excel_columns:
        col_str = str(col).strip()
        col_lower = col_str.lower()
        
        # Check direct mappings first (exact matches)
        if col_str in direct_mappings:
            mapping[col] = direct_mappings[col_str]
            continue
            
        # Check simple mappings
        mapped = False
        for keyword, target in simple_mappings.items():
            if keyword in col_lower:
                mapping[col] = target
                mapped = True
                break
        
        # Check group mappings
        if not mapped:
            for keyword, target in group_mappings.items():
                if keyword in col_lower:
                    mapping[col] = target
                    break
    
    return mapping

def convert_excel_to_json():
    """Convert Excel data to JSON format with predefined structure"""
    # Path to the Excel file
    excel_path = os.path.join('data', 'self-reported-mental-health-college-students-2022', 'Raw data.xlsx')
    
    try:
        print("Reading Excel file...")
        
        # Based on examination, the questions are in row 1 (header=1)
        df = pd.read_excel(excel_path, header=1)
        print(f"Successfully loaded: {len(df)} rows, {len(df.columns)} columns")
        
        print("Excel columns:", list(df.columns)[:10])  # Show first 10 columns
        
        # Get the predefined question metadata
        question_metadata = get_question_metadata()
        
        # Automatically map Excel columns to JSON structure
        column_mapping = auto_map_columns(df.columns)
        
        print("Column mapping found:")
        for excel_col, json_key in list(column_mapping.items())[:10]:
            print(f"  {excel_col} -> {json_key}")
        
        # Convert data
        data = {
            "questions": question_metadata,
            "responses": []
        }
        
        print("Processing responses...")
        for idx, (_, row) in enumerate(df.iterrows()):
            answers = {}
            
            # Process each mapped column
            for excel_col, json_mapping in column_mapping.items():
                if excel_col not in row.index:
                    continue
                    
                value = row[excel_col]
                
                # Clean and validate the value
                if pd.isna(value) or value is None:
                    continue
                    
                # Convert to float if possible
                try:
                    value = float(value)
                except:
                    value = clean_text(str(value))
                    if value == '' or value.lower() == 'nan':
                        continue
                
                # Map to JSON structure
                if isinstance(json_mapping, str):
                    # Simple mapping
                    answers[json_mapping] = value
                elif isinstance(json_mapping, tuple):
                    # Group mapping
                    group_key, sub_key = json_mapping
                    if group_key not in answers:
                        answers[group_key] = {}
                    answers[group_key][sub_key] = value
            
            # Only add response if it has data
            if answers:
                response = {
                "respondent": str(idx + 1),
                    "answers": answers
            }
            data["responses"].append(response)
        
        # Create output directory
        output_dir = os.path.join('preprocessed_data', 'self-repoted-mental-health-college-students-2022')
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to JSON file
        json_path = os.path.join(output_dir, 'mental_health_questionnaire.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ JSON saved to: {json_path}")
        print(f"Total responses: {len(data['responses'])}")
        print(f"Sample response keys: {list(data['responses'][0]['answers'].keys()) if data['responses'] else 'No responses'}")
        
        return json_path
        
    except FileNotFoundError:
        print(f"Error: File not found at {excel_path}")
        print("Please make sure the file exists in the correct location.")
    except Exception as e:
        print(f"Error processing the file: {str(e)}")
        import traceback
        traceback.print_exc()

def convert_json_to_html(json_path, output_dir):
    """Convert JSON data to HTML format matching the specified structure"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Start HTML content
        html_content = "<h1>Questions</h1>\n<ul>\n"
        
        # Add questions section
        for question_key, question_data in data['question_metadata'].items():
            if isinstance(question_data, dict):
                # Complex question with base question and sub-questions
                html_content += f"  <li><strong>{question_key}:</strong>\n"
                html_content += f"    <p>{question_data['base_question']}</p>\n"
                html_content += "    <ul>\n"
                for sub_key, sub_question in question_data["sub_questions"].items():
                    html_content += f"      <li>{sub_key}: {sub_question}</li>\n"
                html_content += "    </ul>\n"
                html_content += "  </li>\n"
            else:
                # Simple question
                html_content += f"  <li><strong>{question_key}:</strong> {question_data}</li>\n"
        
        html_content += "</ul>\n\n"
        
        # Add responses section
        html_content += "<h1>Responses</h1>\n"
        
        for response in data['responses']:
            html_content += f"<h2>Respondent {response['respondent']}</h2>\n"
            html_content += "<ul>\n"
            
            # Get all question keys to ensure we show missing answers
            all_question_keys = data['question_metadata'].keys()
            
            for question_key in all_question_keys:
                if question_key in response['answers']:
                    answer_value = response['answers'][question_key]
                    
                    if isinstance(answer_value, dict):
                        # Grouped answer (like Parental Education)
                        html_content += f"  <li><strong>{question_key}:</strong>\n"
                        html_content += "    <ul>\n"
                        for sub_key, sub_value in answer_value.items():
                            html_content += f"      <li>{sub_key}: {sub_value}</li>\n"
                        html_content += "    </ul>\n"
                        html_content += "  </li>\n"
                    else:
                        # Simple answer
                        html_content += f"  <li><strong>{question_key}:</strong> {answer_value}</li>\n"
                else:
                    # Missing answer
                    html_content += f"  <li><strong>{question_key}:</strong> (missing)</li>\n"
            
            html_content += "</ul>\n\n"
        
        # Save HTML file
        html_path = os.path.join(output_dir, 'mental_health_questionnaire.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML saved to: {html_path}")
        return html_path
        
    except Exception as e:
        print(f"Error creating HTML: {e}")
        return None

def convert_json_to_xml(json_path, output_dir):
    """Convert JSON data to simple XML format"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        xml_content = '<questionnaire>\n'
        
        # Add questions
        xml_content += '  <questions>\n'
        for question_key, question_data in data['question_metadata'].items():
            xml_content += f'    <question>\n'
            xml_content += f'      <title>{question_key}</title>\n'
            
            if isinstance(question_data, dict):
                xml_content += f'      <text>{question_data["base_question"]}</text>\n'
                for sub_key, sub_question in question_data["sub_questions"].items():
                    xml_content += f'      <subquestion>\n'
                    xml_content += f'        <title>{sub_key}</title>\n'
                    xml_content += f'        <text>{sub_question}</text>\n'
                    xml_content += f'      </subquestion>\n'
            else:
                xml_content += f'      <text>{question_data}</text>\n'
            
            xml_content += f'    </question>\n'
        xml_content += '  </questions>\n'
        
        # Add responses
        xml_content += '  <responses>\n'
        for response in data['responses']:
            xml_content += f'    <response id="{response["respondent"]}">\n'
            
            for answer_key, answer_value in response['answers'].items():
                xml_content += f'      <answer>\n'
                xml_content += f'        <question>{answer_key}</question>\n'
                
                if isinstance(answer_value, dict):
                    for sub_key, sub_value in answer_value.items():
                        xml_content += f'        <subanswer>\n'
                        xml_content += f'          <question>{sub_key}</question>\n'
                        xml_content += f'          <value>{sub_value}</value>\n'
                        xml_content += f'        </subanswer>\n'
                else:
                    xml_content += f'        <value>{answer_value}</value>\n'
                
                xml_content += f'      </answer>\n'
            
            xml_content += f'    </response>\n'
        xml_content += '  </responses>\n'
        xml_content += '</questionnaire>\n'
        
        # Save XML file
        xml_path = os.path.join(output_dir, 'mental_health_questionnaire.xml')
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
        
        md_content = "# Mental Health Questionnaire\n\n"
        
        # Add questions
        md_content += "## Questions\n\n"
        
        for question_key, question_data in data['question_metadata'].items():
            md_content += f"### {question_key}\n\n"
            
            if isinstance(question_data, dict):
                md_content += f"{question_data['base_question']}\n\n"
                for sub_key, sub_question in question_data["sub_questions"].items():
                    md_content += f"- {sub_key}: {sub_question}\n"
                md_content += "\n"
            else:
                md_content += f"{question_data}\n\n"
        
        # Add responses
        md_content += "## Responses\n\n"
        
        for response in data['responses']:
            md_content += f"### Respondent {response['respondent']}\n\n"
            
            for answer_key, answer_value in response['answers'].items():
                if isinstance(answer_value, dict):
                    md_content += f"**{answer_key}:**\n"
                    for sub_key, sub_value in answer_value.items():
                        md_content += f"- {sub_key}: {sub_value}\n"
                    md_content += "\n"
                else:
                    md_content += f"**{answer_key}:** {answer_value}\n\n"
        
        # Save Markdown file
        md_path = os.path.join(output_dir, 'mental_health_questionnaire.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✓ Markdown saved to: {md_path}")
        return md_path
        
    except Exception as e:
        print(f"Error creating Markdown: {e}")
        return None

def convert_json_to_txt(json_path, output_dir):
    """Convert JSON data to simple plain text format"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        txt_content = "MENTAL HEALTH QUESTIONNAIRE\n\n"
        
        # Add questions
        txt_content += "QUESTIONS\n"
        txt_content += "---------\n\n"
        
        for question_key, question_data in data['question_metadata'].items():
            txt_content += f"{question_key}\n"
            
            if isinstance(question_data, dict):
                txt_content += f"{question_data['base_question']}\n"
                for sub_key, sub_question in question_data["sub_questions"].items():
                    txt_content += f"  - {sub_key}: {sub_question}\n"
                txt_content += "\n"
            else:
                txt_content += f"{question_data}\n\n"
        
        # Add responses
        txt_content += "RESPONSES\n"
        txt_content += "---------\n\n"
        
        for response in data['responses']:
            txt_content += f"Respondent {response['respondent']}\n"
            
            for answer_key, answer_value in response['answers'].items():
                if isinstance(answer_value, dict):
                    txt_content += f"{answer_key}:\n"
                    for sub_key, sub_value in answer_value.items():
                        txt_content += f"  {sub_key}: {sub_value}\n"
                else:
                    txt_content += f"{answer_key}: {answer_value}\n"
            
            txt_content += "\n"
        
        # Save TXT file
        txt_path = os.path.join(output_dir, 'mental_health_questionnaire.txt')
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
    parser = argparse.ArgumentParser(description='Convert mental health dataset to questionnaire formats')
    
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
    
    # Convert Excel to JSON (always done as base format)
    json_path = convert_excel_to_json()
    
    # If JSON conversion was successful, convert to requested formats
    if json_path:
        output_dir = os.path.join('preprocessed_data', 'self-repoted-mental-health-college-students-2022')
        convert_to_specific_formats(json_path, output_dir, formats_to_generate)
