import sqlite3
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import csv
import json
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Azure AI credentials
text_analytics_key = "beb426be64af4d5181ecff4801816f72"
text_analytics_endpoint = "https://pylanguage.cognitiveservices.azure.com/"
speech_key = "9c84dbbed4474be4b5f2dfbfcc53b5d3"
speech_region = "eastus"

# Initialize the Azure AI Text Analytics client
text_analytics_client = TextAnalyticsClient(endpoint=text_analytics_endpoint, credential=AzureKeyCredential(text_analytics_key))

# Initialize the Azure AI Speech config
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)

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

# Voice input function with automatic language detection using Azure
def get_voice_input(audio_file_path):
    # Create a speech recognizer with auto language detection (limited to 4 languages)
    auto_detect_source_language_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-US", "es-ES", "fr-FR", "de-DE"])
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, 
        auto_detect_source_language_config=auto_detect_source_language_config,
        audio_config=audio_config
    )

    print("Processing audio file...")
    
    # Start speech recognition
    result = speech_recognizer.recognize_once_async().get()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        detected_language = result.properties.get(speechsdk.PropertyId.SpeechServiceConnection_AutoDetectSourceLanguageResult)
        print(f"Detected language: {detected_language}")
        print("Transcribed text: " + result.text)
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized in the audio file")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")

    return None

# Remove the main() function and if __name__ == "__main__" block

# Modify the retrieve_memories function to accept an optional memory_id parameter
def retrieve_memories(keyword=None, category=None, start_date=None, end_date=None, sentiment=None, language=None, memory_id=None):
    conn = sqlite3.connect('memory.db')
    c = conn.cursor()
    
    query = "SELECT * FROM memories WHERE 1=1"
    params = []
    
    if memory_id:
        query += " AND id = ?"
        params.append(memory_id)
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

# Modify the export_memories function to return the filename
def export_memories(format='csv'):
    memories = retrieve_memories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'csv':
        filename = f'memories_export_{timestamp}.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Content', 'Timestamp', 'Category'])
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
