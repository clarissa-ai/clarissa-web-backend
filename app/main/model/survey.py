from .. import db, flask_bcrypt

import datetime

class Survey(db.Model):
    """Survey model for representing surveys"""
    __tablename__ = "survey"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column(db.Boolean, default=False, nullable=False)
    main = db.Column(db.Boolean, default=False, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    image_link = db.Column(db.String(300))

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', foreign_keys='Survey.author_id')

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1000), nullable=False)

    root = db.relationship('Question', uselist=False, backref='parent')

    questions = db.relationship('Question', backref='survey')
    responses = db.relationship('Response', backref='survey')
    links = db.relationship('Link', backref='survey')
    summaries = db.relationship('Summary', backref='survey')

    def get_json(self):
        r_id = -1
        if self.root:
            r_id = str(self.root.id) 
        return {
            'title': self.title,
            'description': self.description,
            'root_id': str(r_id),
            'image_url': '',
            'links': [l.get_json() for l in self.links],
            'questions': [q.get_json() for q in self.questions],
            'summaries': [s.get_json() for s in self.summaries]
        }

    def __repr__(self):
        return "<Survey '{}'>".format(self.title)

    @staticmethod
    def get_active_surveys():
        return Survey.query.filter_by(active=True).all()

    @staticmethod
    def get_main_survey():
        return Survey.query.filter_by(active=True, main=True).first()

class Link(db.Model):
    """Link model for Survey title page"""
    __tablename__ = "link"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    image_link = db.Column(db.String(300))
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))

    def get_json(self):
        return {
            'title': self.title,
            'description': self.description,
            'link': self.link,
            'image_url': ''
        }

class Question(db.Model):
    """Question model for representing survey questions"""
    __tablename__ = "question"

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
    next_type = db.Column(db.String(100))
    title = db.Column(db.String(200), nullable=False)

    def get_json(self):
        return {
            'title': str(self.title),
            'next': str(next_id)
        }

    def __repr__(self):
        return "<Option '{}'>".format(self.title)

class Summary(db.Model):
    """Summary model for representing final summaries of surveys"""
    __tablename__ = "summary"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))
    info_groups = db.relationship('SummaryInfoGroup', backref='summary')
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))

    def __repr__(self):
        return "<Summary '{}'>".format(self.title)

    def get_json(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'info_groups': [g.get_json()  for g in self.info_groups]
        }

class SummaryInfoGroup(db.Model):
    """Group model for representing lists of info in final summaries"""
    __tablename__ = "summaryinfogroup"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    link_URL = db.Column(db.String(300), nullable=False)
    details = db.relationship('SummaryDetail', backref='summary')
    summary_id = db.Column(db.Integer, db.ForeignKey('summary.id'))

    def __repr__(self):
        return "<SummaryInfoGroup '{}'>".format(self.title)

    def get_json(self):
        return {
            'title': self.title,
            'details': [str(d.text) for d in self.details]
        }

class SummaryDetail(db.Model):
    """Detail model for representing details in a summary info group"""
    __tablename__ = "summarydetail"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(500), nullable=False)
    infogroup_id = db.Column(db.Integer, db.ForeignKey('summaryinfogroup.id'))

    def __repr__(self):
        return "<SummaryDetail '{}'>".format(self.text)



class Response(db.Model):
    """Response model for representing survey responses"""
    __tablename__ = "response"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))
    json_response = db.Column(db.Text)