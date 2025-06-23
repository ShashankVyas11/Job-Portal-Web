from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    usertype = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    
    posted_jobs = db.relationship('Jobs', backref='company', lazy=True, cascade="all, delete")  # ← updated
    applications = db.relationship('Application', backref='application_submiter', lazy=True, cascade="all, delete")
    
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.usertype}', '{self.email}')"



class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    degree = db.Column(db.String(20), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    cv = db.Column(db.String(20), nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(20), default="Submitted")  # Possible: Submitted, Rejected


    def __repr__(self):
        return f"Application('{self.id}','{self.gender}', '{self.date_posted}', '{self.degree}', '{self.industry}', '{self.experience}', '{self.user_id}', '{self.job_id}')"

class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)

    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ← stays same
    applications = db.relationship('Application', backref='application_jober', lazy=True, cascade="all, delete")
    
    salary = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Jobs('{self.id}', '{self.title}', '{self.industry}', '{self.date_posted}')"





    def __repr__(self):
        return f"Jobs('{self.id}','{self.title}', '{self.industry}', '{self.date_posted}')"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    review = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Review('{self.username}', '{self.review}')"
