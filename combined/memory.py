from app import db
from datetime import datetime

class Memory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(50))
    sentiment = db.Column(db.String(20))
    sentiment_scores = db.Column(db.Text)
    entities = db.Column(db.Text)
    key_phrases = db.Column(db.Text)
    language = db.Column(db.String(50))
    language_code = db.Column(db.String(10))

    def __repr__(self):
        return f'<Memory {self.id}>'
