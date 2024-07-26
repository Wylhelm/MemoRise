from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import json
import logging
import os

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    # Configure logging
    logging.basicConfig(level=logging.DEBUG)
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

    app.logger.info('Starting the Memory Augmentation App')
    app.logger.info(f'Template folder: {os.path.abspath(app.template_folder)}')
    app.logger.info(f'Static folder: {os.path.abspath(app.static_folder)}')

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes import main_routes, memory_routes, export_routes, analytics_routes

    app.register_blueprint(main_routes.bp)
    app.register_blueprint(memory_routes.bp)
    app.register_blueprint(export_routes.bp)
    app.register_blueprint(analytics_routes.bp)
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(memory_routes.bp)
    app.register_blueprint(export_routes.bp)
    app.register_blueprint(analytics_routes.bp)

    @app.template_filter('from_json')
    def from_json_filter(value):
        try:
            return json.loads(value)
        except Exception as e:
            app.logger.error(f"Error in from_json_filter: {str(e)}")
            return value

    app.logger.info('App initialization complete')
    return app
