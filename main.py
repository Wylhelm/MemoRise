import sqlite3
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import csv
import json
import speech_recognition as sr
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.textanalytics import DetectLanguageInput

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Azure AI Text Analytics credentials
key = "beb426be64af4d5181ecff4801816f72"
endpoint = "https://pylanguage.cognitiveservices.azure.com/"

# Initialize the Azure AI Text Analytics client
text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Database setup
def setup_database():
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memories
                 (id INTEGER PRIMARY KEY, 
                  content TEXT, 
                  timestamp TEXT, 
                  category TEXT, 
                  sentiment TEXT,
                  sentiment_scores TEXT,
                  entities TEXT,
                  key_phrases TEXT,
                  language TEXT,
                  language_code TEXT)''')
    conn.commit()
    conn.close()

# Enhanced NLP categorization
def enhanced_categorize_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    word_counts = Counter(tokens)
    
    categories = {
        'Work': ['job', 'office', 'meeting', 'project', 'deadline', 'colleague', 'boss', 'client'],
        'Family': ['family', 'mom', 'dad', 'sister', 'brother', 'child', 'kids', 'parents'],
        'Health': ['doctor', 'exercise', 'diet', 'medication', 'symptom', 'health', 'illness'],
        'Finance': ['money', 'bank', 'savings', 'investment', 'budget', 'expense', 'income'],
        'Education': ['school', 'study', 'learn', 'teacher', 'student', 'class', 'course', 'exam'],
        'Travel': ['trip', 'vacation', 'flight', 'hotel', 'tour', 'visit', 'journey', 'destination'],
    }
    
    category_scores = {category: sum(word_counts.get(keyword, 0) for keyword in keywords)
                       for category, keywords in categories.items()}
    
    return max(category_scores, key=category_scores.get) if any(category_scores.values()) else 'General'

# Text input function
def add_memory(content):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    category = enhanced_categorize_text(content)
    
    # Perform Azure AI analysis
    sentiment, confidence = analyze_sentiment(content)
    entities = recognize_entities(content)
    key_phrases = extract_key_phrases(content)
    language, language_code = detect_language(content)
    
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("""INSERT INTO memories 
                 (content, timestamp, category, sentiment, sentiment_scores, entities, key_phrases, language, language_code) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (content, timestamp, category, sentiment, 
               json.dumps(confidence.__dict__), 
               json.dumps(entities), 
               json.dumps(key_phrases),
               language,
               language_code))
    conn.commit()
    conn.close()
    return c.lastrowid

# Enhanced retrieval function
def retrieve_memories(keyword=None, category=None, start_date=None, end_date=None, sentiment=None, language=None):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    
    query = "SELECT * FROM memories WHERE 1=1"
    params = []
    
    if keyword:
        query += " AND content LIKE ?"
        params.append(f'%{keyword}%')
    if category:
        query += " AND category = ?"
        params.append(category)
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)
    if sentiment:
        query += " AND sentiment = ?"
        params.append(sentiment)
    if language:
        query += " AND language = ?"
        params.append(language)
    
    query += " ORDER BY timestamp DESC"
    
    c.execute(query, params)
    memories = c.fetchall()
    conn.close()
    return memories

# Update memory function
def update_memory(memory_id, new_content):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    new_category = enhanced_categorize_text(new_content)
    c.execute("UPDATE memories SET content = ?, category = ? WHERE id = ?",
              (new_content, new_category, memory_id))
    conn.commit()
    conn.close()
    return c.rowcount > 0

# Delete memory function
def delete_memory(memory_id):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    c.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
    conn.commit()
    conn.close()
    return c.rowcount > 0

# Sentiment Analysis function
def analyze_sentiment(text):
    result = text_analytics_client.analyze_sentiment([text])[0]
    return result.sentiment, result.confidence_scores

# Named Entity Recognition function
def recognize_entities(text):
    result = text_analytics_client.recognize_entities([text])[0]
    return [(entity.text, entity.category) for entity in result.entities]

# Key Phrase Extraction function
def extract_key_phrases(text):
    result = text_analytics_client.extract_key_phrases([text])[0]
    return result.key_phrases

# Language Detection function
def detect_language(text):
    result = text_analytics_client.detect_language([text])[0]
    return result.primary_language.name, result.primary_language.iso6391_name

# Export memories function
def export_memories(format='csv'):
    memories = retrieve_memories()  # Retrieve all memories
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'csv':
        filename = f'memories_export_{timestamp}.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Content', 'Timestamp', 'Category'])  # Header
            for memory in memories:
                writer.writerow(memory)
    
    elif format == 'json':
        filename = f'memories_export_{timestamp}.json'
        memories_list = [
            {
                'id': memory[0],
                'content': memory[1],
                'timestamp': memory[2],
                'category': memory[3]
            } for memory in memories
        ]
        with open(filename, 'w') as file:
            json.dump(memories_list, file, indent=2)
    
    else:
        raise ValueError("Unsupported export format. Use 'csv' or 'json'.")
    
    return filename

# Voice input function
def get_voice_input():
    with sr.Microphone() as source:
        print("Listening... Speak your memory.")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print("You said: " + text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            print("Sorry, there was an error connecting to the speech recognition service.")
            return None

# Main command-line interface
def main():
    setup_database()
    while True:
        print("\n1. Add a new memory (text)")
        print("2. Add a new memory (voice)")
        print("3. Retrieve memories")
        print("4. Update a memory")
        print("5. Delete a memory")
        print("6. Export memories")
        print("7. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            content = input("Enter your memory: ")
            memory_id = add_memory(content)
            print(f"Memory added successfully! ID: {memory_id}")
        
        elif choice == '2':
            content = get_voice_input()
            if content:
                memory_id = add_memory(content)
                print(f"Memory added successfully! ID: {memory_id}")
        
        elif choice == '3':
            keyword = input("Enter a keyword to search (or press enter for all): ")
            category = input("Enter a category to filter (or press enter for all): ")
            start_date = input("Enter start date (YYYY-MM-DD) or press enter to skip: ")
            end_date = input("Enter end date (YYYY-MM-DD) or press enter to skip: ")
            sentiment = input("Enter sentiment to filter (positive/neutral/negative) or press enter to skip: ")
            language = input("Enter language to filter or press enter to skip: ")
        
            memories = retrieve_memories(keyword, category, start_date, end_date, sentiment, language)
            if memories:
                for memory in memories:
                    print(f"ID: {memory[0]}, [{memory[2]}] {memory[1]}")
                    print(f"Category: {memory[3]}")
                    print(f"Sentiment: {memory[4]}")
                    print(f"Language: {memory[8]} ({memory[9]})")
                    print(f"Key Phrases: {', '.join(json.loads(memory[7]))}")
                    print(f"Entities: {', '.join([f'{e[0]} ({e[1]})' for e in json.loads(memory[6])])}")
                    print("---")
            else:
                print("No memories found matching the criteria.")
    
        elif choice == '4':
            memory_id = input("Enter the ID of the memory to update: ")
            new_content = input("Enter the new content for the memory: ")
            if update_memory(memory_id, new_content):
                print("Memory updated successfully!")
            else:
                print("Failed to update memory. Please check the ID and try again.")
    
        elif choice == '5':
            memory_id = input("Enter the ID of the memory to delete: ")
            if delete_memory(memory_id):
                print("Memory deleted successfully!")
            else:
                print("Failed to delete memory. Please check the ID and try again.")
    
        elif choice == '6':
            format = input("Enter export format (csv/json): ").lower()
            try:
                filename = export_memories(format)
                print(f"Memories exported successfully to {filename}")
            except ValueError as e:
                print(f"Export failed: {str(e)}")
    
        elif choice == '7':
            print("Thank you for using the Memory Augmentation App. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
