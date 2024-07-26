from flask import Blueprint, render_template
import logging

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    logging.info("Accessing the index route")
    return render_template('index.html')

@bp.route('/home')
def home():
    logging.info("Accessing the home route")
    return render_template('index.html')
