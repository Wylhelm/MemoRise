from flask import Blueprint, render_template, current_app
import logging

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    current_app.logger.info("Accessing the index route")
    try:
        return render_template('index.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering index.html: {str(e)}")
        return "An error occurred while rendering the page.", 500

@bp.route('/home')
def home():
    current_app.logger.info("Accessing the home route")
    try:
        return render_template('index.html')
    except Exception as e:
        current_app.logger.error(f"Error rendering index.html: {str(e)}")
        return "An error occurred while rendering the page.", 500
