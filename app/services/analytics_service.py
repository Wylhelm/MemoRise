from app.models.memory import Memory
from app import db
import pandas as pd
from collections import Counter
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def get_sentiment_trends(interval='W', date=None):
    if date is None:
        date = datetime.now()

    try:
        memories = Memory.query.order_by(Memory.timestamp).all()
        if not memories:
            logger.warning("No memories found in the database.")
            return None  # Return None if there are no memories

        df = pd.DataFrame([(m.timestamp, m.sentiment) for m in memories], columns=['timestamp', 'sentiment'])
        logger.info(f"Created DataFrame with {len(df)} rows.")
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Convert sentiment to numeric values
        sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
        df['sentiment_numeric'] = df['sentiment'].map(sentiment_map)

        # Filter data based on the interval
        if interval == 'M':
            start_date = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            x_label = 'Day'
            date_format = '%d'
        elif interval == 'W':
            start_date = date - timedelta(days=date.weekday())
            end_date = start_date + timedelta(days=6)
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            x_label = 'Day'
            date_format = '%a'
        elif interval == 'D':
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1) - timedelta(seconds=1)
            date_range = pd.date_range(start=start_date, end=end_date, freq='h')
            x_label = 'Hour'
            date_format = '%H:00'

        df_filtered = df[(df.index >= start_date) & (df.index <= end_date)]
        df_resampled = df_filtered['sentiment_numeric'].resample('h').mean().reindex(date_range).fillna(0)

        data = {
            'labels': df_resampled.index.strftime(date_format).tolist(),
            'values': df_resampled.tolist(),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'x_label': x_label
        }

        # Add error handling
        if df_resampled.empty:
            data['labels'] = []
            data['values'] = []

        return data

    except Exception as e:
        logger.error(f"Error in get_sentiment_trends: {str(e)}")
        return None

def get_memory_insights():
    memories = Memory.query.all()
    
    if not memories:
        return {
            'top_entities': {},
            'top_categories': {},
            'top_phrases': {}
        }

    # Most mentioned entities
    all_entities = [entity for memory in memories for entity in json.loads(memory.entities) if isinstance(entity, str)]
    all_entities += [entity[0] for memory in memories for entity in json.loads(memory.entities) if isinstance(entity, list) and len(entity) > 0]
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
