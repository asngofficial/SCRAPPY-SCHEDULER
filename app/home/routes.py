from flask import render_template, jsonify, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from datetime import datetime, timezone, timedelta
from app import db
from app.models import Task
from app.home import bp
from app.home.forms import TaskForm
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
        form = TaskForm()
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
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        try:
            # Convert to timezone-aware datetimes
            start_date = form.start_date.data.replace(tzinfo=timezone.utc)
            due_date = form.due_date.data.replace(tzinfo=timezone.utc)
            
            task = Task(
                task_name=escape(form.task_name.data.strip()),
                start_date=start_date,
                due_date=due_date,
                user_id=current_user.id
            )
            
            db.session.add(task)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'task': task.to_dict()
            })

        except ValueError as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
            
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error: {str(e)}")
            return jsonify({
                'success': False,
                'message': "Failed to save task. Please try again."
            }), 500
            
    return jsonify({
        'success': False,
        'errors': form.errors
    }), 400


@bp.route('/update-task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
        
        if request.headers.get('Content-Type') == 'application/json':
            data = request.get_json()
            form = TaskForm(data=data, meta={'csrf': False})
        else:
            form = TaskForm()
        
        if form.validate_on_submit():
            task.task_name = escape(form.task_name.data.strip())
            
            # Handle both string and datetime inputs
            start_date = form.start_date.data
            due_date = form.due_date.data
            
            task.start_date = datetime.strptime(
                start_date if isinstance(start_date, str) else start_date.strftime('%Y-%m-%dT%H:%M'),
                '%Y-%m-%dT%H:%M'
            ).replace(tzinfo=timezone.utc)
            
            task.due_date = datetime.strptime(
                due_date if isinstance(due_date, str) else due_date.strftime('%Y-%m-%dT%H:%M'),
                '%Y-%m-%dT%H:%M'
            ).replace(tzinfo=timezone.utc)
            
            db.session.commit()
            return jsonify({'success': True})
        
        return jsonify({
            'success': False,
            'errors': form.errors
        }), 400

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating task: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update task'
        }), 500

@bp.route('/task/<int:task_id>')
@login_required
def get_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
        return jsonify({
            'success': True,
            'task': {
                'id': task.id,
                'task_name': task.task_name,
                'start_date': task.start_date.isoformat(),
                'due_date': task.due_date.isoformat()
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching task {task_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to fetch task details'}), 500

@bp.route('/delete-task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Task deleted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting task {task_id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to delete task'}), 500
