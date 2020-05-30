from flask import Flask
from app import db
from passlib.hash import pbkdf2_sha256 as sha256

'''
USER DATABASE TABLES
-------------------
User class represents all the information stored on a user

User fields:
  - "id" --> unique user id
  - "first_name" --> user's first name
  - "last_name --> user's last name
  - "age" --> average of inputted age range
  - "email" --> unique user email
  - "password" --> hashed password string
  - "reports" --> link to all of the users reports
'''
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False, index = True)
    password = db.Column(db.String(120), nullable = False)
    reports = db.relationship('Report', backref = 'user')
    symptoms = db.relationship('Symptom', backref = 'user')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email = email).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'first_name': x.first_name,
                'email': x.email,
                'age': x.age,
                'symptom_count': len(x.symptoms),
                'password': x.password
            }
        return {'users': list(map(lambda x: to_json(x), User.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

# Model that stores all removed tokens
class RevokedTokenModel(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key = True)
    jti = db.Column(db.String(120))
    
    def add(self):
        db.session.add(self)
        db.session.commit()
    
    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti = jti).first()
        return bool(query)



'''
CORE API DATABASE TABLES
------------------------

REPORT: Record for every sickness that a user has

SYMPTOM: 1 record for every symptom 

'''
class Report(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    date = db.Column(db.Date)
    symptoms = db.relationship('Symptom', backref = 'report')
    comments = db.relationship('Comment', backref = 'report')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id = id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {
                'title': x.title,
                'date': x.date.strftime("%m/%d/%Y"),
                'symptoms': [{'name':s.name, 'date':s.datetime.strftime("%m/%d/%Y, %H:%M:%S"), 'severity':s.severity} for s in x.symptoms],
                'comments': [{'text': c.text, 'datetime': c.datetime.strftime("%m/%d/%Y, %H:%M:%S")} for c in x.comments],
                'user': x.user.first_name
            }
        return {'reports': list(map(lambda x: to_json(x), Report.query.all()))}

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
    text = db.Column(db.Text)
    datetime = db.Column(db.DateTime)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

class Symptom(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    datetime = db.Column(db.DateTime)
    severity = db.Column(db.Integer)
    data = db.Column(db.String(400)) # could be int for fever temp or string for description of symptom --> handle in other api endpoint logic
    api_id = db.Column(db.Integer)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
