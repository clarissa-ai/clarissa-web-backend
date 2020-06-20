from .. import db


class Survey(db.Model):
    """Survey model for representing surveys"""
    __tablename__ = "survey"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    active = db.Column(db.Boolean, default=False, nullable=False)
    main = db.Column(db.Boolean, default=False, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', foreign_keys='Survey.author_id')

    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(1000), nullable=False)

    image_file = db.Column(db.LargeBinary)
    image_type = db.Column(db.String(4))

    root_id = db.Column(db.Integer)

    questions = db.relationship('Question', backref='survey')
    responses = db.relationship('Response', backref='survey')
    links = db.relationship('Link', backref='survey')
    summaries = db.relationship('Summary', backref='survey')

    def get_image_url(self):
        url = '/api/images/get_image/filler/fill.png'
        if self.image_file:
            url = '/api/images/get_image/survey/{}.{}'.format(
                self.id,
                self.image_type
            )
        return url

    def get_json(self):
        r_id = -1
        if self.root_id:
            r_id = self.root_id
        return {
            'title': self.title,
            'description': self.description,
            'root_id': r_id,
            'image_url': self.get_image_url(),
            'question_count': len(self.questions),
            'links': [link.get_json() for link in self.links],
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

    image_file = db.Column(db.LargeBinary)
    image_type = db.Column(db.String(4))

    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))

    def get_image_url(self):
        url = '/api/images/get_image/filler/fill.png'
        if self.image_file:
            url = "/api/images/get_image/survey_link/{}.{}".format(
                self.id,
                self.image_type
            )
        return url

    def get_json(self):
        return {
            'title': self.title,
            'description': self.description,
            'link': self.link,
            'image_url': self.get_image_url()
        }


# DICTIONARIES FOR QUESTION TYPE DEFINITIONS
question_type_dict = {
    'single_select': 'Single Select',
    'multiple_select': 'Multiple Select',
    'short_answer': 'Short Answer',
    'dropdown': 'Dropdown',
    'dropdown_from_dataset': 'Dropdown from Dataset'
}

question_description_dict = {
    'single_select': "Single Select",
    'multiple_select': 'Multiple Select',
    'short_answer': 'Short Answer',
    'dropdown': 'Dropdown',
    'dropdown_from_dataset': 'Dropdown from Dataset'
}


class Question(db.Model):
    """Question model for representing survey questions"""
    __tablename__ = "question"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(400))
    type = db.Column(db.String(100), nullable=False)
    options = db.relationship('Option', backref='question')

    default_next_id = db.Column(db.Integer)

    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))

    @staticmethod
    def get_type_list():
        list = []
        for key, val in question_type_dict.items():
            list.append((key, val))
        return list

    def display_type(self):
        return question_type_dict[self.type]

    def display_type_description(self):
        return question_description_dict[self.type]

    def get_json(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'description': self.description,
            'default_next': self.default_next_id or -1,
            'options': [o.get_json() for o in self.options]
        }

    def __repr__(self):
        return "<Question '{}'>".format(self.title)


class Option(db.Model):
    """Option model for representing question options"""
    __tablename__ = "option"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    # ID of next question -- default to question's default_next_id if no ID
    next_id = db.Column(db.Integer)

    # Weights to summaries that an option is related to
    summary_id = db.Column(db.Integer)
    summary_weight = db.Column(db.Integer)

    def get_json(self):
        response_object = {
            'title': self.title
        }
        if self.next_id:
            response_object['next_id'] = self.next_id
        if self.summary_id:
            response_object['summary_id'] = self.summary_id
            response_object['summary_weight'] = self.summary_weight or 0
        return response_object

    def __repr__(self):
        return "<Option '{}'>".format(self.title)


class Summary(db.Model):
    """Summary model for representing final summaries of surveys"""
    __tablename__ = "summary"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500))

    image_file = db.Column(db.LargeBinary)
    image_type = db.Column(db.String(4))

    info_groups = db.relationship('SummaryInfoGroup', backref='summary')
    survey_id = db.Column(db.Integer, db.ForeignKey('survey.id'))

    def get_image_url(self):
        url = '/api/images/get_image/filler/fill.png'
        if self.image_file:
            url = "/api/images/get_image/survey_link/{}.{}".format(
                self.id,
                self.image_type
            )
        return url

    def __repr__(self):
        return "<Summary '{}'>".format(self.title)

    def get_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'image_url': self.get_image_url(),
            'info_groups': [g.get_json() for g in self.info_groups]
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
            'link_URL': self.link_URL,
            'details': [str(d.text) for d in self.details],
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
    json_response = db.Column(db.JSON)
