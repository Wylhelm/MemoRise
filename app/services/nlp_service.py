from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from config import Config
import os

# Initialize the Azure AI Text Analytics client
text_analytics_client = TextAnalyticsClient(
    endpoint=Config.TEXT_ANALYTICS_ENDPOINT, 
    credential=AzureKeyCredential(Config.TEXT_ANALYTICS_KEY)
)

if not Config.TEXT_ANALYTICS_KEY or not Config.TEXT_ANALYTICS_ENDPOINT:
    raise ValueError("Azure Text Analytics credentials are not set. Please check your .env file.")

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

def analyze_sentiment(text):
    result = text_analytics_client.analyze_sentiment([text])[0]
    return result.sentiment, result.confidence_scores

def recognize_entities(text):
    result = text_analytics_client.recognize_entities([text])[0]
    return [(entity.text, entity.category) for entity in result.entities]

def extract_key_phrases(text):
    result = text_analytics_client.extract_key_phrases([text])[0]
    return result.key_phrases

def detect_language(text):
    result = text_analytics_client.detect_language([text])[0]
    return result.primary_language.name, result.primary_language.iso6391_name
