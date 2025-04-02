import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from datetime import datetime
import clicksend_client
from clicksend_client import SmsMessage
from clicksend_client.rest import ApiException
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from flask import Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

# Load environment variables
load_dotenv()

# Define base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize the database
db = SQLAlchemy(model_class=Base)

# Configure ClickSend API
configuration = clicksend_client.Configuration()
configuration.username = os.getenv("CLICKSEND_USERNAME")
configuration.password = os.getenv("CLICKSEND_PASSWORD")
api_instance = clicksend_client.SMSApi(clicksend_client.ApiClient(configuration))

# Database Models
class User(db.Model, UserMixin):  # Added UserMixin
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    tasks = db.relationship("Task", back_populates="user", cascade="all, delete-orphan", lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(120), nullable=False)
    assigned_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="tasks")

    def to_dict(self):
        return {
            'id': self.id,
            'task_name': self.task_name,
            'assigned_date': self.assigned_date.isoformat(),
            'due_date': self.due_date.isoformat()
        }

# Create Flask application
app = Flask(__name__, 
           template_folder='app/templates',
           static_folder='app/static')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Route to redirect unauthorized users

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)

# Blueprint Setup
home = Blueprint("home", __name__)
auth = Blueprint("auth", __name__)

@home.route("/")
@login_required  # Now using Flask-Login's decorator
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()  # Changed to current_user
    return render_template("index.html", tasks=tasks)

@home.route("/tasks", methods=["GET"])
@login_required
def get_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([task.to_dict() for task in tasks])

@home.route("/add_task", methods=["POST"])
@login_required
def add_task():
    try:
        data = request.form
        task_name = data["task_name"]
        assigned_date = datetime.fromisoformat(data["assigned_date"])
        due_date = datetime.fromisoformat(data["due_date"])

        if assigned_date > due_date:
            return jsonify({"error": "Assigned date cannot be after due date"}), 400

        new_task = Task(
            task_name=task_name,
            assigned_date=assigned_date,
            due_date=due_date,
            user_id=current_user.id  # Changed to current_user
        )
        db.session.add(new_task)
        db.session.commit()
        
        return jsonify(new_task.to_dict()), 201

    except ValueError as e:
        return jsonify({"error": "Invalid date format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@home.route("/update_task/<int:task_id>", methods=["POST"])
@login_required
def update_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        if task.user_id != current_user.id:  # Changed to current_user
            return jsonify({"error": "Unauthorized"}), 403
            
        data = request.form
        
        task.task_name = data["task_name"]
        task.assigned_date = datetime.fromisoformat(data["assigned_date"])
        task.due_date = datetime.fromisoformat(data["due_date"])
        
        if task.assigned_date > task.due_date:
            return jsonify({"error": "Assigned date cannot be after due date"}), 400
            
        db.session.commit()
        return jsonify(task.to_dict())

    except ValueError as e:
        return jsonify({"error": "Invalid date format"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@home.route("/delete_task/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        if task.user_id != current_user.id:  # Changed to current_user
            return jsonify({"error": "Unauthorized"}), 403
            
        db.session.delete(task)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Auth routes
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash("Invalid email or password", "error")
            return redirect(url_for("auth.login"))
            
        login_user(user)  # Flask-Login's login function
        return redirect(url_for("home.index"))
        
    return render_template("signin.html")

@auth.route("/logout")
@login_required
def logout():
    logout_user()  # Flask-Login's logout function
    return redirect(url_for("auth.login"))

# Helper function to send reminders
def send_reminder(task):
    sms_message = SmsMessage(
        source="SCRAPPY SCHEDULER",
        body=f"Reminder: Your task '{task.task_name}' is due at {task.due_date}.",
        to=os.getenv("RECIPIENT_PHONE"),
    )
    sms_messages = clicksend_client.SmsMessageCollection(messages=[sms_message])
    
    try:
        api_instance.sms_send_post(sms_messages)
    except ApiException as e:
        print(f"Failed to send SMS: {e}")

# Register blueprints
app.register_blueprint(home)
app.register_blueprint(auth)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # Create a default user if none exists
        if not User.query.first():
            default_user = User(username="default", email="default@example.com")
            default_user.set_password("password")
            db.session.add(default_user)
            db.session.commit()
    app.run(debug=True)