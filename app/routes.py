from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from flask_login import current_user, login_required
from werkzeug.exceptions import BadRequest
from app.models import Task, db
from sqlalchemy.exc import SQLAlchemyError
from html import escape
from app.home.forms import TaskForm  # Add this import


from app.email import send_notification_email


home = Blueprint("home", __name__)

def validate_task_input(task_name, start_date_str, due_date_str):
    """Validate and sanitize task input data"""
    if not all([task_name, start_date_str, due_date_str]):
        raise ValueError("All fields are required")
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M")
        due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValueError("Invalid date format")
    
    if start_date > due_date:
        raise ValueError("Assigned date cannot be after due date")
    
    # Sanitize task name
    sanitized_task_name = escape(task_name.strip())
    if not sanitized_task_name:
        raise ValueError("Task name cannot be empty")
    
    return sanitized_task_name, start_date, due_date

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

@home.route("/add-task", methods=["POST"])
@login_required
def add_task():
    print("Add task endpoint hit")  # Debug
    form = TaskForm()
    
    # if not form.validate_on_submit():
    #     print("Form validation failed:", form.errors)  # Debug
    #     return jsonify({
    #         "success": False,
    #         "errors": form.errors
    #     }), 400

    # try:
    #     print("Creating task...")  # Debug
    #     task = Task(
    #         task_name=form.task_name.data,
    #         start_date=form.start_date.data,
    #         due_date=form.due_date.data,
    #         user_id=current_user.id
    #     )
    #     db.session.add(task)
    #     db.session.commit()
    #     print("Task saved successfully")  # Debug

    if form.validate_on_submit():
        print("✅ Form is valid")

        task = Task(
            title=form.title.data,
            description=form.description.data,
            start_date=form.start_date.data,
            due_date=form.due_date.data,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()

        flash("Task created!", "success")
        return redirect(url_for("main.index"))
        
    send_notification_email(
        current_user.email,
        "🗓️ New Task Added",
        f"Hi {current_user.username},\n\nYour task '{task.title}' has been added to Scrappy Scheduler!"
    )
    flash("Task created and email sent!")

        # return jsonify({"success": True})

    print("❌ Form validation failed")
    print("Errors:", form.errors)
    flash("Form failed: " + str(form.errors), "danger")
    return redirect(url_for("main.index"))
        
    # except Exception as e:
    #     db.session.rollback()
    #     print("Error saving task:", str(e))  # Debug
    #     return jsonify({
    #         "success": False,
    #         "error": str(e)
    #     }), 500

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
        start_date_str = request.form.get("start_date")
        due_date_str = request.form.get("due_date")

        sanitized_name, start_date, due_date = validate_task_input(
            task_name, start_date_str, due_date_str
        )

        task.task_name = sanitized_name
        task.start_date = start_date
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