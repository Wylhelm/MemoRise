from flask import Blueprint, render_template, request, jsonify
from app.services.analytics_service import get_sentiment_trends, get_memory_insights
from datetime import datetime, timedelta

bp = Blueprint('analytics', __name__)

@bp.route('/analytics')
def analytics():
    interval = request.args.get('interval', 'W')
    date = request.args.get('date')
    if date:
        date = datetime.strptime(date, '%Y-%m-%d')
    else:
        date = datetime.now()
    sentiment_trends = get_sentiment_trends(interval, date)
    memory_insights = get_memory_insights()
    return render_template('analytics.html', sentiment_trends=sentiment_trends, memory_insights=memory_insights, current_date=date, interval=interval)

@bp.route('/get_sentiment_trends')
def get_sentiment_trends_route():
    interval = request.args.get('interval', 'W')
    date = request.args.get('date')
    if date:
        date = datetime.strptime(date, '%Y-%m-%d')
    else:
        date = datetime.now()
    sentiment_trends = get_sentiment_trends(interval, date)
    return jsonify(sentiment_trends)
