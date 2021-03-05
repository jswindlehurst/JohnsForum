import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))

# from models import dbsettings

class User(db.Model):
    # __tablename__ = 'forum_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String, unique=True)
    session_token = db.Column(db.String, unique=False)
    active = db.Column(db.Integer, unique=False)