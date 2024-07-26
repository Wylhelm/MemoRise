from flask import Blueprint, render_template, request
from app.services.analytics_service import get_sentiment_trends, get_memory_insights

bp = Blueprint('analytics', __name__)

@bp.route('/analytics')
def analytics():
    interval = request.args.get('interval', 'W')
    sentiment_trends = get_sentiment_trends(interval)
    memory_insights = get_memory_insights()
    print("Sentiment Trends:", sentiment_trends)  # Debug print
    print("Memory Insights:", memory_insights)  # Debug print
    return render_template('analytics.html', sentiment_trends=sentiment_trends, memory_insights=memory_insights)
