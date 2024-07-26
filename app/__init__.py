from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import json

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    from app.routes import main_routes, memory_routes, export_routes
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(memory_routes.bp)
    app.register_blueprint(export_routes.bp)

    @app.template_filter('from_json')
    def from_json_filter(value):
        try:
            return json.loads(value)
        except:
            return value

    return app
