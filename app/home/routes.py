from flask import render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Task
from app.home import bp
from app.home.forms import TaskForm  # Add this import
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import BadRequest
from html import escape

def validate_task_data(task_name, due_date_str):
    """Validate and sanitize task input"""
    if not task_name or not due_date_str:
        raise ValueError("All fields are required")
    
    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%dT%H:%M")
    except ValueError:
        raise ValueError("Invalid date format")
    
    if due_date < datetime.utcnow():
        raise ValueError("Due date cannot be in the past")
    
    return escape(task_name.strip()), due_date

@bp.route('/')
@login_required
def index():
    try:
        tasks = Task.query.filter_by(user_id=current_user.id)\
                         .order_by(Task.due_date.asc())\
                         .all()
        form = TaskForm()  # Initialize form
        return render_template('index.html', tasks=tasks, form=form)
    except SQLAlchemyError:
        flash('Error loading tasks. Please try again.', 'error')
        return render_template('index.html', tasks=[], form=TaskForm())

@bp.route('/api/tasks')
@login_required
def get_tasks():
    try:
        tasks = Task.query.filter_by(user_id=current_user.id)\
                         .order_by(Task.due_date.asc())\
                         .all()
        return jsonify([{
            'id': task.id,
            'task_name': task.task_name,
            'due_date': task.due_date.isoformat(),
            'is_completed': task.is_completed
        } for task in tasks])
    except SQLAlchemyError:
        return jsonify({'error': 'Failed to fetch tasks'}), 500

@bp.route('/add-task', methods=['POST'])
@login_required
# def add_task():
#     form = TaskForm()
#     if form.validate_on_submit():
#         try:
#             task = Task(
#                 task_name=escape(form.task_name.data.strip()),
#                 due_date=form.due_date.data,
#                 user_id=current_user.id,
#                 is_completed=False
#             )
            
#             db.session.add(task)
#             db.session.commit()
#             flash('Task added successfully!', 'success')
#             return redirect(url_for('home.index'))
        
#         except (SQLAlchemyError, BadRequest):
#             db.session.rollback()
#             flash('Failed to add task. Please try again.', 'error')
#     else:
#         for field, errors in form.errors.items():
#             for error in errors:
#                 flash(f"{getattr(form, field).label.text}: {error}", 'error')
    
#     return redirect(url_for('home.index'))

def add_task():
    form = TaskForm()

    if form.validate_on_submit():
        task = Task(
            task_name=form.task_name.data,
            start_date=form.start_date.data,
            due_date=form.due_date.data,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()

        return jsonify(success=True)

    print("Task form validation failed")
    print(form.errors)

    return jsonify(success=False, errors=form.errors), 400

@bp.route('/update-task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
        
        if 'is_completed' in request.form:
            task.is_completed = request.form['is_completed'] == 'true'
        else:
            form = TaskForm()
            if form.validate_on_submit():
                task.task_name = escape(form.task_name.data.strip())
                task.due_date = form.due_date.data
            else:
                return jsonify({'errors': form.errors}), 400
        
        db.session.commit()
        return jsonify({'success': True})
    
    except (SQLAlchemyError, BadRequest):
        db.session.rollback()
        return jsonify({'error': 'Failed to update task'}), 500

@bp.route('/delete-task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('Failed to delete task. Please try again.', 'error')
    
    return redirect(url_for('home.index'))