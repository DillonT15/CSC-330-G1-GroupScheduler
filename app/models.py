from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime

group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('study_group_id', db.Integer, db.ForeignKey('study_group.id'), primary_key=True))



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100))
    major = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)

class StudyGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    time = db.Column(db.String(100))
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

class Thread(db.Model):
    thread_id = db.Column(db.Integer, primary_key=True) #Should this be a thread id? or just id, and for the prior class ids the same question
    title = db.Column(db.String(100), nullable=False)
    #messages = db.relationship('Message', backref='thread', lazy=True) #? add messages
    study_group_id = db.Column(db.Integer, db.ForeignKey('study_group.id'), nullable=False)

class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.thread_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description =  db.Column(db.Text)
    meeting_time = db.Column(db.String(100))

    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
