from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from typing import TYPE_CHECKING, Any, Optional

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    usertype = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    jobs = db.relationship('Jobs', backref='job_applier', lazy=True)
    applications = db.relationship('Application', backref='application_submiter', lazy=True)

    if TYPE_CHECKING:
        def __init__(
            self,
            id: Optional[int] = None,
            username: Optional[str] = None,
            usertype: Optional[str] = None,
            email: Optional[str] = None,
            password: Optional[str] = None,
            jobs: Any = None,
            applications: Any = None,
            **kwargs: Any
        ) -> None: ...

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.usertype}', '{self.email}')"


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(20), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    degree = db.Column(db.String(20), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    cv = db.Column(db.String(100), nullable=False)
    cover_letter = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)

    if TYPE_CHECKING:
        def __init__(
            self,
            id: Optional[int] = None,
            gender: Optional[str] = None,
            date_posted: Optional[datetime] = None,
            degree: Optional[str] = None,
            industry: Optional[str] = None,
            experience: Optional[int] = None,
            cv: Optional[str] = None,
            cover_letter: Optional[str] = None,
            user_id: Optional[int] = None,
            job_id: Optional[int] = None,
            application_submiter: Any = None,
            application_jober: Any = None,
            **kwargs: Any
        ) -> None: ...

    def __repr__(self):
        return f"Application('{self.id}','{self.gender}', '{self.date_posted}', '{self.degree}', '{self.industry}', '{self.experience}', '{self.user_id}', '{self.job_id}')"


class Jobs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    applications = db.relationship('Application', backref='application_jober', lazy=True)

    if TYPE_CHECKING:
        def __init__(
            self,
            id: Optional[int] = None,
            title: Optional[str] = None,
            industry: Optional[str] = None,
            description: Optional[str] = None,
            date_posted: Optional[datetime] = None,
            user_id: Optional[int] = None,
            job_applier: Any = None,
            applications: Any = None,
            **kwargs: Any
        ) -> None: ...

    def __repr__(self):
        return f"Jobs('{self.id}','{self.title}', '{self.industry}', '{self.date_posted}')"


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    review = db.Column(db.Text, nullable=False)

    if TYPE_CHECKING:
        def __init__(
            self,
            id: Optional[int] = None,
            username: Optional[str] = None,
            review: Optional[str] = None,
            **kwargs: Any
        ) -> None: ...

    def __repr__(self):
        return f"Review('{self.username}', '{self.review}')"
