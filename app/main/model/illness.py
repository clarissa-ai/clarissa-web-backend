from .. import db


class Illness(db.Model):
    __tablename__ = 'illness'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    symptoms = db.relationship('Symptom', backref='illness')

    active = db.Column(db.Boolean, nullable=False, default=True)

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now()
    )

    def get_json(self):
        return {
            'active': self.active,
            'created_on': self.created_on,
            'updated_on': self.updated_on,
            'symptoms': [s.get_json() for s in self.symptoms],
            # 'diagnosis': self.diagnoses.last()
        }


class Symptom(db.Model):
    __tablename__ = 'symptom'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    illness_id = db.Column(
        db.Integer,
        db.ForeignKey('illness.id'),
        nullable=False
    )

    # TODO: specify formats for JSON
    # {
    #   severity: <int>
    # }
    data = db.Column(db.JSON)

    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now()
    )

    def get_json(self):
        return {
            'title': self.title,
            'created_on': self.created_on,
            'updated_on': self.updated_on
        }
