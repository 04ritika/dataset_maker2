import json
import uuid
from googletrans import Translator

# Function to read paragraphs from a file with line numbers
def read_paragraphs(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        paragraphs = []
        current_paragraph = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line:
                current_paragraph.append(stripped_line)
            else:
                if current_paragraph:
                    paragraphs.append("\n".join(current_paragraph))
                    current_paragraph = []
        if current_paragraph:
            paragraphs.append("\n".join(current_paragraph))
        return paragraphs
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

# Function to load data from a JSON file
def load_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading data from file {file_path}: {e}")
        return []

# Function to translate text to Hindi if it's in English
def translate_text_to_hindi(text):
    # Check if the text contains Hindi characters
    if any('\u0900' <= char <= '\u097f' for char in text):
        # Text contains Hindi characters, assuming it's already in Hindi
        return text
    else:
        # Translate text to Hindi
        translator = Translator()
        translated = translator.translate(text, src='en', dest='hi')
        return translated.text

# Function to get user input for questions and answers
def get_questions_and_answers(paragraphs, existing_data):
    data = []
    for paragraph in paragraphs:
        entry = None
        for item in existing_data:
            if item['paragraph'] == paragraph:
                entry = item
                break
        if entry is None:
            entry = {
                'id': str(uuid.uuid4()),
                'paragraph': paragraph,
                'qa_pairs': []
            }
        while True:
            question = input(f"Enter a question for the paragraph: \n{paragraph}\n(or type 'done' to finish): ")
            if question.lower() == 'done':
                break
            question_translated = translate_text_to_hindi(question)
            answer = input("Enter the answer to the question: ")
            answer_translated = translate_text_to_hindi(answer)
            
            # Calculate the start and end indices of the answer in the paragraph
            answer_start_index = paragraph.find(answer_translated)
            if answer_start_index != -1:
                answer_end_index = answer_start_index + len(answer_translated)
            else:
                print("The answer was not found in the paragraph. Please re-enter the question and answer.")
                continue

            entry['qa_pairs'].append({
                'question': question_translated,
                'answer': answer_translated,
                'context': {
                    'source': 'user_input',  # Example metadata
                    'answer_start_index': answer_start_index,
                    'answer_end_index': answer_end_index
                }
            })
        data.append(entry)
    return data

# Function to save data to a JSON file
def save_data(file_path, new_data):
    try:
        existing_data = load_data(file_path)
        for new_entry in new_data:
            # Check if the paragraph already exists in the existing data
            existing_entry = next((entry for entry in existing_data if entry['paragraph'] == new_entry['paragraph']), None)
            if existing_entry:
                # For each new question-answer pair, check if it already exists in the existing entry
                for qa_pair in new_entry['qa_pairs']:
                    if qa_pair not in existing_entry['qa_pairs']:
                        # If the question-answer pair does not exist, add it to the existing entry
                        existing_entry['qa_pairs'].append(qa_pair)
            else:
                # If the paragraph does not exist, add the new entry to the existing data
                existing_data.append(new_entry)
        
        # Save the updated data to the file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)
        
        print(f"Data has been saved to {file_path}")
    except Exception as e:
        print(f"Error saving data to file {file_path}: {e}")

def main():
    # Step 1: Read paragraphs from a file
    paragraphs_file = r'C:\Users\cuckoo\Desktop\java ritika\paragraphs.txt'
    paragraphs = read_paragraphs(paragraphs_file)
    
    if not paragraphs:
        print("No paragraphs to process. Exiting.")
        return

    # Step 2: Load existing data from JSON file
    existing_data_file = r'C:\Users\cuckoo\Desktop\java ritika\paragraphs_with_qa.json'
    existing_data = load_data(existing_data_file)

    # Step 3: Get questions and answers from the user
    data = get_questions_and_answers(paragraphs, existing_data)

    # Step 4: Save the structured data to the JSON file
    save_data(existing_data_file, data)

if __name__ == '__main__':
    main()
