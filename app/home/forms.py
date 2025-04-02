from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime

class TaskForm(FlaskForm):
    task_name = StringField('Task Name', validators=[DataRequired()])
    start_date = DateTimeLocalField('Start Date', 
                                 format='%Y-%m-%dT%H:%M',
                                 validators=[DataRequired()],
                                 default=datetime.utcnow)
    due_date = DateTimeLocalField('Due Date',
                                format='%Y-%m-%dT%H:%M',
                                validators=[DataRequired()],
                                default=datetime.utcnow)
    submit = SubmitField('Save Task')  # Add this submit field