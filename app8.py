from flask import Flask, render_template, request, session
import json
import os
from googletrans import Translator
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for the session

# Set the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# File paths
paragraphs_file = os.path.join(base_dir, 'data', 'cleaned_data.json')
save_data_file = os.path.join(base_dir, 'data', 'q_and_Ans2.json')
index_file = os.path.join(base_dir, 'data', 'current_index.txt')

# Function to load paragraphs from a JSON file
def load_paragraphs(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(f"Error loading paragraphs from file {file_path}: {e}")
        return {}

# Function to translate text to Hindi if it's in English
def translate_text_to_hindi(text):
    if any('\u0900' <= char <= '\u097f' for char in text):
        return text
    else:
        translator = Translator()
        translated = translator.translate(text, src='en', dest='hi')
        return translated.text

# Function to save data to a JSON file
def save_data(file_path, new_data):
    try:
        existing_data = load_paragraphs(file_path)
        for new_entry in new_data:
            existing_entry = next((entry for entry in existing_data if entry['id'] == new_entry['id']), None)
            if existing_entry:
                for qa_pair in new_entry['qa_pairs']:
                    if qa_pair not in existing_entry['qa_pairs']:
                        existing_entry['qa_pairs'].append(qa_pair)
            else:
                existing_data.append(new_entry)
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)
        print(f"Data has been saved to {file_path}")
    except Exception as e:
        print(f"Error saving data to file {file_path}: {e}")

# Function to save the current index to a file
def save_current_index(index):
    try:
        with open(index_file, 'w') as file:
            file.write(str(index))
    except Exception as e:
        print(f"Error saving current index to file {index_file}: {e}")

# Function to load the current index from a file
def load_current_index():
    if os.path.exists(index_file):
        try:
            with open(index_file, 'r') as file:
                return int(file.read().strip())
        except Exception as e:
            print(f"Error loading current index from file {index_file}: {e}")
    return 0

# Helper function to check if a paragraph has QA pairs
def paragraph_has_qa(paragraph):
    existing_data = load_paragraphs(save_data_file)
    for entry in existing_data:
        if entry['paragraph'] == paragraph and len(entry['qa_pairs']) > 0:
            return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    paragraphs = load_paragraphs(paragraphs_file)
    current_index = load_current_index()

    if request.method == 'POST':
        paragraph_id = request.form['paragraph_id']
        paragraph = request.form['paragraph']
        qa_pairs = json.loads(request.form['qa_pairs'])

        new_qa_pairs = []
        for qa_pair in qa_pairs:
            question = qa_pair['question']
            answer = qa_pair['answer']
            
            question_translated = translate_text_to_hindi(question)
            answer_translated = translate_text_to_hindi(answer)

            answer_start_index = paragraph.find(answer_translated)
            if answer_start_index != -1:
                answer_end_index = answer_start_index + len(answer_translated)
            else:
                return "The answer was not found in the paragraph. Please re-enter the question and answer."

            new_qa_pairs.append({
                'question': question_translated,
                'answer': answer_translated,
                'context': {
                    'source': 'user_input',
                    'answer_start_index': answer_start_index,
                    'answer_end_index': answer_end_index
                }
            })

        new_data = [{
            'id': paragraph_id,
            'paragraph': paragraph,
            'qa_pairs': new_qa_pairs
        }]
        
        save_data(save_data_file, new_data)
        current_index += 1  # Move to the next paragraph
        save_current_index(current_index)

    if paragraphs:
        keys = list(paragraphs.keys())
        
        # Loop to find the first paragraph without Q&A pairs
        while current_index < len(keys) and paragraph_has_qa(paragraphs[keys[current_index]]):
            current_index += 1
        
        if current_index >= len(paragraphs):
            return "All paragraphs have been processed."

        save_current_index(current_index)
        current_paragraph_key = keys[current_index]
        current_paragraph = paragraphs[current_paragraph_key]
        paragraph_id = str(uuid.uuid4())

        # Check if paragraph already exists in the saved data
        existing_data = load_paragraphs(save_data_file)
        existing_entry = next((entry for entry in existing_data if entry['paragraph'] == current_paragraph), None)
        if existing_entry:
            paragraph_id = existing_entry['id']

        return render_template('index8.html', paragraph=current_paragraph, paragraph_id=paragraph_id, index=current_index, num_paragraphs=len(paragraphs))
    else:
        return "No paragraphs available."

@app.route('/view_data', methods=['GET'])
def view_data():
    data = load_paragraphs(save_data_file)
    return render_template('view_data.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
