from models.dbsettings import db

class Topic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=False)
    text = db.Column(db.String, unique=False)
    created = db.Column(db.String, unique=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    creator = db.relationship("User", foreign_keys=creator_id)


    @classmethod
    def create(cls, title, text, created, creator):
        topic = cls(title=title, text=text, created=created, creator=creator)

        db.add(topic)
        db.commit()

        return topic