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
    assigned_date = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='tasks')

    def __repr__(self):
        return f'<Task {self.task_name}>'

    def to_dict(self):
        """Serialize task object to dictionary"""
        return {
            'id': self.id,
            'task_name': self.task_name,
            'assigned_date': self.assigned_date.isoformat(),
            'due_date': self.due_date.isoformat(),
            'user_id': self.user_id,
            'is_completed': self.is_completed
        }

    @classmethod
    def create_task(cls, task_name, due_date, user_id, assigned_date=None):
        """Helper method to create new tasks"""
        if not assigned_date:
            assigned_date = datetime.utcnow()
            
        if assigned_date > due_date:
            raise ValueError("Assigned date cannot be after due date")
            
        task = cls(
            task_name=task_name,
            assigned_date=assigned_date,
            due_date=due_date,
            user_id=user_id
        )
        db.session.add(task)
        return task

    def update(self, task_name=None, assigned_date=None, due_date=None):
        """Update task attributes"""
        if task_name:
            self.task_name = task_name
        if assigned_date:
            if due_date and assigned_date > due_date:
                raise ValueError("Assigned date cannot be after due date")
            self.assigned_date = assigned_date
        if due_date:
            if assigned_date and assigned_date > due_date:
                raise ValueError("Assigned date cannot be after due date")
            self.due_date = due_date
        return self