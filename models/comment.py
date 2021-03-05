from models.dbsettings import db


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, unique=False)
    created = db.Column(db.String, unique=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    author = db.relationship("User", foreign_keys=author_id)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    topic = db.relationship("Topic", foreign_keys=topic_id)