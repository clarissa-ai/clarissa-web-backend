from .. import db
import datetime

class Action(db.Model):
    """Table for storing admin dashbord records"""
    __tablename__ = "action"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('adminuser.id'))
    datetime = db.Column(db.DateTime, nullable=False)
    text = db.Column(db.Text)