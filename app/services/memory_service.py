from app.models.memory import Memory
from app import db
from app.services.nlp_service import enhanced_categorize_text, analyze_sentiment, recognize_entities, extract_key_phrases, detect_language
from datetime import datetime
import json
import csv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def add_memory(content):
    timestamp = datetime.now()  # Use current system time instead of UTC
    category = enhanced_categorize_text(content)
    sentiment, confidence = analyze_sentiment(content)
    entities = recognize_entities(content)
    key_phrases = extract_key_phrases(content)
    language, language_code = detect_language(content)

    memory = Memory(
        content=content,
        timestamp=timestamp,
        category=category,
        sentiment=sentiment,
        sentiment_scores=json.dumps(confidence.__dict__),
        entities=json.dumps(entities),
        key_phrases=json.dumps(key_phrases),
        language=language,
        language_code=language_code
    )

    db.session.add(memory)
    db.session.commit()
    return memory.id

def retrieve_memories(keyword=None, category=None, start_date=None, end_date=None, sentiment=None, language=None, memory_id=None):
    query = Memory.query

    if memory_id:
        query = query.filter(Memory.id == memory_id)
    if keyword:
        query = query.filter(Memory.content.like(f'%{keyword}%'))
    if category:
        query = query.filter(Memory.category == category)
    if start_date:
        query = query.filter(Memory.timestamp >= start_date)
    if end_date:
        query = query.filter(Memory.timestamp <= end_date)
    if sentiment:
        query = query.filter(Memory.sentiment == sentiment)
    if language:
        query = query.filter(Memory.language == language)

    return query.order_by(Memory.timestamp.desc()).all()

def update_memory(memory_id, new_content):
    memory = Memory.query.get(memory_id)
    if memory:
        memory.content = new_content
        memory.category = enhanced_categorize_text(new_content)
        memory.sentiment, confidence = analyze_sentiment(new_content)
        memory.sentiment_scores = json.dumps(confidence.__dict__)
        memory.entities = json.dumps(recognize_entities(new_content))
        memory.key_phrases = json.dumps(extract_key_phrases(new_content))
        memory.language, memory.language_code = detect_language(new_content)
        db.session.commit()
        return True
    return False

def delete_memory(memory_id):
    memory = Memory.query.get(memory_id)
    if memory:
        db.session.delete(memory)
        db.session.commit()
        return True
    return False

def export_memories(format='csv'):
    memories = Memory.query.all()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    export_dir = 'exports'
    os.makedirs(export_dir, exist_ok=True)
    
    if format == 'csv':
        filename = os.path.join(export_dir, f'memories_export_{timestamp}.csv')
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ID', 'Content', 'Timestamp', 'Category', 'Sentiment', 'Language'])
            for memory in memories:
                writer.writerow([memory.id, memory.content, memory.timestamp, memory.category, memory.sentiment, memory.language])
    
    elif format == 'json':
        filename = os.path.join(export_dir, f'memories_export_{timestamp}.json')
        memories_list = [
            {
                'id': memory.id,
                'content': memory.content,
                'timestamp': memory.timestamp.isoformat(),
                'category': memory.category,
                'sentiment': memory.sentiment,
                'language': memory.language
            } for memory in memories
        ]
        with open(filename, 'w') as file:
            json.dump(memories_list, file, indent=2)
    
    else:
        raise ValueError("Unsupported export format. Use 'csv' or 'json'.")
    
    return filename

def get_relevant_memories(query, top_n=5):
    """
    Retrieve the most relevant memories based on the user's query.
    """
    memories = Memory.query.all()
    memory_contents = [memory.content for memory in memories]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(memory_contents + [query])
    
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
    most_similar_indices = cosine_similarities.argsort()[-top_n:][::-1]
    
    return [memories[i] for i in most_similar_indices]
