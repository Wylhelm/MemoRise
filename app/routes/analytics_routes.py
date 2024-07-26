from flask import Blueprint, render_template
from app.services.analytics_service import get_sentiment_trends, get_memory_insights

bp = Blueprint('analytics', __name__)

@bp.route('/analytics')
def analytics():
    sentiment_trends = get_sentiment_trends()
    memory_insights = get_memory_insights()
    return render_template('analytics.html', sentiment_trends=sentiment_trends, memory_insights=memory_insights)
