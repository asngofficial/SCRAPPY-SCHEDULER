from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired, Length  # Added Length import
from datetime import datetime, timedelta
from wtforms.validators import ValidationError

class TaskForm(FlaskForm):
    task_name = StringField('Task Name', validators=[
        DataRequired(),
        Length(min=2, max=128)
    ])
    start_date = DateTimeLocalField('Start Date', 
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()],
        default=datetime.utcnow
    )
    due_date = DateTimeLocalField('Due Date',
        format='%Y-%m-%dT%H:%M',
        validators=[
            DataRequired()
        ],
        default=lambda: datetime.utcnow() + timedelta(hours=1)
    )
    submit = SubmitField('Save Task')

    def validate_due_date(form, field):
        if field.data < form.start_date.data:
            raise ValidationError('Due date must be after start date')