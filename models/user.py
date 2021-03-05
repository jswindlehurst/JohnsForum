

from models.dbsettings import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String, unique=True)
    session_token = db.Column(db.String, unique=False)
    active = db.Column(db.Integer, unique=False)