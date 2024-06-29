import requests
from bs4 import BeautifulSoup
import re
import json

def save_user_paragraphs_to_file(file_path, paragraphs):
    try:
        # Read existing data if any
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # Append new paragraphs to the data
    data.extend(paragraphs)

    # Save the updated data to the JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_paragraphs_from_user():
    paragraphs = []
    while True:
        paragraph = input("Enter a paragraph (or type 'done' to finish): ").strip()
        if paragraph.lower() == 'done':
            break
        paragraphs.append(paragraph)
    return paragraphs

def get_paragraphs_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().split('\n\n')
        paragraphs = [para.strip() for para in content if para.strip()]
        return paragraphs
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

def get_paragraphs_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract paragraphs and clean the text
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.get_text()
            text = re.sub(r'\[\d+\]', '', text)  # Remove citations like [22]
            text = re.sub(r'http\S+', '', text)  # Remove links
            if text.strip():
                paragraphs.append(text.strip())
        return paragraphs
    except Exception as e:
        print(f"Error retrieving URL {url}: {e}")
        return []

def main():
    file_path = r'C:\Users\cuckoo\Desktop\flask_project\paragraphs3.json'
    choice = input("Do you want to enter paragraphs manually, from a file, or from a URL? (manual/file/url): ").strip().lower()

    if choice == 'manual':
        paragraphs = get_paragraphs_from_user()
    elif choice == 'file':
        input_file_path = input("Enter the path to the file: ").strip()
        paragraphs = get_paragraphs_from_file(input_file_path)
    elif choice == 'url':
        url = input("Enter the URL: ").strip()
        paragraphs = get_paragraphs_from_url(url)
    else:
        print("Invalid choice. Exiting.")
        return

    if paragraphs:
        save_user_paragraphs_to_file(file_path, paragraphs)
        print(f"Paragraphs have been saved to {file_path}")
    else:
        print("No paragraphs to save.")

if __name__ == '__main__':
    main()
