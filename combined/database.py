from app import db

def setup_database():
    db.create_all()
