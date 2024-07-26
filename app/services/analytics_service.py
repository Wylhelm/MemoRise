from app.models.memory import Memory
from app import db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from collections import Counter
import json

def get_sentiment_trends():
    memories = Memory.query.order_by(Memory.timestamp).all()
    df = pd.DataFrame([(m.timestamp, m.sentiment) for m in memories], columns=['timestamp', 'sentiment'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    df = df.resample('D').agg(lambda x: x.value_counts().index[0])

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x=df.index, y='sentiment')
    plt.title('Sentiment Trends Over Time')
    plt.xlabel('Date')
    plt.ylabel('Sentiment')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return plot_url

def get_memory_insights():
    memories = Memory.query.all()
    
    # Most mentioned entities
    all_entities = [entity for memory in memories for entity in json.loads(memory.entities)]
    entity_counts = Counter(all_entities)
    top_entities = dict(entity_counts.most_common(10))

    # Common themes (using categories as themes)
    category_counts = Counter([memory.category for memory in memories])
    top_categories = dict(category_counts.most_common(5))

    # Key phrases over time
    all_phrases = [phrase for memory in memories for phrase in json.loads(memory.key_phrases)]
    phrase_counts = Counter(all_phrases)
    top_phrases = dict(phrase_counts.most_common(10))

    return {
        'top_entities': top_entities,
        'top_categories': top_categories,
        'top_phrases': top_phrases
    }
