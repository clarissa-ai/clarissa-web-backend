from .. import db, flask_bcrypt

import datetime

class Survey(db.Model):
    """Survey model for representing surveys"""
    __tablename__ = "survey"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column(db.Boolean, default=False, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', foreign_keys='Survey.author_id')

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(400), nullable=False)

    root = db.relationship('Question', uselist=False, backref='parent')

    questions = db.relationship('Question', backref='survey')

    def get_json(self):
        return {
            'title': self.title,
            'description': self.description,
            'root': self.root_id,
            'questions': [q.get_json() for q in this.questions]
        }

    def __repr__(self):
        return "<Survey '{}'>".format(self.title)

class Question(db.Model):
    """Question model for representing survey questions"""
    ___tablename__ = "question"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(400))
    type = db.Column(db.String(100), nullable=False)
    options = db.relationship('Option', backref='question')

    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))

    def get_json(self):
        return {
            'id': str(self.id),
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'options': [o.get_json() for o in self.options]
        }

    def __repr__(self):
        return "<Question '{}'>".format(self.title)

class Option(db.Model):
    """Option model for representing question options"""
    __tablename__ = "option"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    next_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    title = db.Column(db.String(200), nullable=False)

    def get_json(self):
        return {
            'title': str(self.title),
            'next': str(next_id)
        }

    def __repr__(self):
        return "<Option '{}'>".format(self.title)

class Response(db.Model):
    """Response model for representing survey responses"""
    __tablename__ = "response"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))
    json_response = db.Column(db.Text)