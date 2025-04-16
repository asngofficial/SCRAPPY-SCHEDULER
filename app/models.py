from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .extensions import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', back_populates='user', cascade='all, delete-orphan', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(128), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='tasks')

    def __repr__(self):
        return f'<Task {self.task_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'task_name': self.task_name,
            'start_date': self.start_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'user_id': self.user_id,
            'is_completed': self.is_completed
        }

    @classmethod
    def create_task(cls, task_name, due_date, user_id, start_date=None):
        if not start_date:
            start_date = datetime.utcnow()
        
        # Ensure dates are timezone-aware
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)
        
        if start_date > due_date:
            raise ValueError("Start date must be before due date")
            
        return cls(
            task_name=task_name,
            start_date=start_date,
            due_date=due_date,
            user_id=user_id
        )

    def update(self, task_name=None, start_date=None, due_date=None):
        if task_name:
            self.task_name = task_name
        if start_date:
            if due_date and start_date > due_date:
                raise ValueError("Start date cannot be after due date")
            self.start_date = start_date
        if due_date:
            if start_date and start_date > due_date:
                raise ValueError("Start date cannot be after due date")
            self.due_date = due_date
        return self