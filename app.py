from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

# Initialize the app with both template and static folders set
app = Flask(
    __name__, 
    template_folder="C:/Users/laolu/OneDrive/Desktop/SCRAPPY SCHEDULER/app/templates",
    static_folder="C:/Users/laolu/OneDrive/Desktop/SCRAPPY SCHEDULER/app/static"
)



# In-memory task list (replace with a database later)
tasks = []

@app.route('/')
def index():
    # Render the tasks on the main page
    return render_template('index.html', tasks=tasks)

@app.route('/add_task', methods=['POST'])
def add_task():
    task_name = request.form['task_name']
    assigned_date = request.form['assigned_date']
    due_date = request.form['due_date']

    # Convert dates from string to datetime objects for validation
    try:
        assigned_date = datetime.strptime(assigned_date, '%Y-%m-%dT%H:%M')
        due_date = datetime.strptime(due_date, '%Y-%m-%dT%H:%M')

        if assigned_date > due_date:
            # Return an error message if the assigned date is later than the due date
            return redirect(url_for('index', error="Assigned date cannot be after due date"))

        # Store task as a dictionary (you can replace this with a database later)
        tasks.append({
            'task_name': task_name,
            'assigned_date': assigned_date.strftime('%Y-%m-%d %H:%M'),
            'due_date': due_date.strftime('%Y-%m-%d %H:%M'),
        })

        # Redirect back to the index route to display updated tasks
        return redirect(url_for('index'))

    except ValueError as e:
        # Handle invalid date format
        return redirect(url_for('index', error="Invalid date format. Please use the correct format."))

@app.route('/delete_task', methods=['POST'])
def delete_task():
    task_id = int(request.form['task_id'])

    # Remove the task by index
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
