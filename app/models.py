from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime

# Association table for many-to-many relationship between users and groups
group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('study_group_id', db.Integer, db.ForeignKey('study_group.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False) #username not required use email
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100))
    major = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False)
    # New fields
    is_verified = db.Column(db.Boolean, default=False)
    
    # Relationships
    owned_groups = db.relationship('StudyGroup', backref='owner', foreign_keys='StudyGroup.op_id')
    posts = db.relationship('Post', backref='author', foreign_keys='Post.user_id')
    # Study groups that this user has joined
    joined_groups = db.relationship('StudyGroup', secondary=group_members, 
                                   backref=db.backref('members', lazy='dynamic'))

class StudyGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    time = db.Column(db.String(100))
    # New fields
    title = db.Column(db.String(100))
    tags = db.Column(db.String(200))
    op_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    threads = db.relationship('Thread', backref='study_group', lazy=True)
    
    def add_member(self, user):
        if user not in self.members.all():
            self.members.append(user)
            return True
        return False
    
    def remove_member(self, user):
        if user in self.members.all():
            self.members.remove(user)
            return True
        return False

class Thread(db.Model):
    thread_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    study_group_id = db.Column(db.Integer, db.ForeignKey('study_group.id'), nullable=False)
    # New fields
    thread_content = db.Column(db.Text)
    tag = db.Column(db.String(50))
    date_and_time = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    posts = db.relationship('Post', backref='thread', lazy=True)

class Post(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.thread_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    meeting_time = db.Column(db.String(100))
    # New fields
    date_and_time = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    # New fields
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    post = db.relationship('Post', backref='messages')

# New classes
class Report(db.Model):
    report_id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    violator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='filed_reports')
    violator = db.relationship('User', foreign_keys=[violator_id], backref='received_reports')

class ViolationType(db.Model):
    violation_code = db.Column(db.Integer, primary_key=True)
    violation_description = db.Column(db.String(200), nullable=False)
    
    # Relationships
    violations = db.relationship('Violation', backref='violation_type', lazy=True)

class Violation(db.Model):
    violation_id = db.Column(db.Integer, primary_key=True)
    violator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    violation_code = db.Column(db.Integer, db.ForeignKey('violation_type.violation_code'), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    violator = db.relationship('User', foreign_keys=[violator_id], backref='violations')
    reporter = db.relationship('User', foreign_keys=[reporter_id], backref='reported_violations')
    message = db.relationship('Message', backref='violations')
    post = db.relationship('Post', backref='violations')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

