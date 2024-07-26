from app.models.memory import Memory
from app import db
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import io
import base64
from collections import Counter
import json

def get_sentiment_trends(interval='W'):
    memories = Memory.query.order_by(Memory.timestamp).all()
    if not memories:
        return None  # Return None if there are no memories

    df = pd.DataFrame([(m.timestamp, m.sentiment) for m in memories], columns=['timestamp', 'sentiment'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Convert sentiment to numeric values
    sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
    df['sentiment_numeric'] = df['sentiment'].map(sentiment_map)

    # Filter data based on the interval
    now = pd.Timestamp.now()
    if interval == 'M':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - pd.DateOffset(months=11)
        end_date = now
        date_range = pd.date_range(start=start_date, end=end_date, freq='M')
        x_label = 'Month'
        date_format = '%b %Y'
    elif interval == 'W':
        start_date = now - pd.Timedelta(days=6)
        end_date = now
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        x_label = 'Day'
        date_format = '%d %b'
    elif interval == 'D':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
        date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        x_label = 'Hour'
        date_format = '%H:00'

    df_filtered = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
    df_resampled = df_filtered.set_index('timestamp').resample(interval)['sentiment_numeric'].mean().reindex(date_range).fillna(0)
    df_resampled = df_resampled.reset_index()

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_resampled, x='timestamp', y='sentiment_numeric', marker='o')

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter(date_format))
    plt.xlabel(x_label)

    plt.xticks(rotation=45)
    plt.title('Sentiment Trends Over Time')
    plt.ylabel('Average Sentiment')
    plt.ylim(-1, 1)  # Set y-axis limits

    # Add horizontal lines for sentiment levels
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
    plt.axhline(y=1, color='green', linestyle=':', alpha=0.7)
    plt.axhline(y=-1, color='red', linestyle=':', alpha=0.7)

    # Add legend
    plt.text(plt.xlim()[1], 1, 'Positive', verticalalignment='center', horizontalalignment='left', color='green')
    plt.text(plt.xlim()[1], 0, 'Neutral', verticalalignment='center', horizontalalignment='left', color='gray')
    plt.text(plt.xlim()[1], -1, 'Negative', verticalalignment='center', horizontalalignment='left', color='red')

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    plt.close()  # Close the plot to free up memory
    return plot_url

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
