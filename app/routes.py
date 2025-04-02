from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import current_user, login_required
from werkzeug.exceptions import BadRequest
from app.models import Task, db
from sqlalchemy.exc import SQLAlchemyError
from html import escape
from app.home.forms import TaskForm  # Add this import

home = Blueprint("home", __name__)

def validate_task_input(task_name, assigned_date_str, due_date_str):
    """Validate and sanitize task input data"""
    if not all([task_name, assigned_date_str, due_date_str]):
        raise ValueError("All fields are required")
    
    try:
        assigned_date = datetime.strptime(assigned_date_str, "%Y-%m-%dT%H:%M")
        due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValueError("Invalid date format")
    
    if assigned_date > due_date:
        raise ValueError("Assigned date cannot be after due date")
    
    # Sanitize task name
    sanitized_task_name = escape(task_name.strip())
    if not sanitized_task_name:
        raise ValueError("Task name cannot be empty")
    
    return sanitized_task_name, assigned_date, due_date

@home.route("/")
@login_required
def index():
    try:
        tasks = Task.query.filter_by(user_id=current_user.id)\
                         .order_by(Task.due_date.asc())\
                         .all()
        return render_template("index.html", tasks=tasks)
    except SQLAlchemyError as e:
        flash("Error loading tasks. Please try again.", "error")
        return render_template("index.html", tasks=[])

@home.route("/add", methods=["POST"])
@login_required
def add_task():
    try:
        task_name = request.form.get("task_name", "")
        assigned_date_str = request.form.get("assigned_date")
        due_date_str = request.form.get("due_date")

        sanitized_name, assigned_date, due_date = validate_task_input(
            task_name, assigned_date_str, due_date_str
        )

        new_task = Task(
            task_name=sanitized_name,
            assigned_date=assigned_date,
            due_date=due_date,
            user_id=current_user.id
        )
        
        db.session.add(new_task)
        db.session.commit()
        flash("Task added successfully", "success")

    except ValueError as e:
        flash(str(e), "error")
    except SQLAlchemyError:
        db.session.rollback()
        flash("Error saving task to database", "error")
    except BadRequest:
        flash("Invalid request data", "error")
    
    return redirect(url_for("home.index"))

@home.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully", "success")
    except SQLAlchemyError:
        db.session.rollback()
        flash("Error deleting task", "error")
    
    return redirect(url_for("home.index"))

@home.route("/update_task/<int:task_id>", methods=["POST"])
@login_required
def update_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
        task_name = request.form.get("task_name", "")
        assigned_date_str = request.form.get("assigned_date")
        due_date_str = request.form.get("due_date")

        sanitized_name, assigned_date, due_date = validate_task_input(
            task_name, assigned_date_str, due_date_str
        )

        task.task_name = sanitized_name
        task.assigned_date = assigned_date
        task.due_date = due_date
        
        db.session.commit()
        flash("Task updated successfully", "success")

    except ValueError as e:
        flash(str(e), "error")
    except SQLAlchemyError:
        db.session.rollback()
        flash("Error updating task", "error")
    except BadRequest:
        flash("Invalid request data", "error")
    
    return redirect(url_for("home.index"))