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
    df = df.set_index('timestamp')

    # Convert sentiment to numeric values
    sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
    df['sentiment_numeric'] = df['sentiment'].map(sentiment_map)

    # Resample and calculate mean sentiment
    df_resampled = df.resample(interval)['sentiment_numeric'].mean().reset_index()

    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_resampled, x='timestamp', y='sentiment_numeric', marker='o')

    # Customize x-axis based on interval
    if interval == 'D':
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    elif interval == 'W':
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%W'))
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MONDAY))
    elif interval == 'M':
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())

    plt.xticks(rotation=45)
    plt.title('Sentiment Trends Over Time')
    plt.xlabel('Date')
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
