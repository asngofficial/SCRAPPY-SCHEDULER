let tempTask = null; // Variable to temporarily store task data during editing

// Open button event listener for the "Add Task" modal
document.querySelector("[data-bs-toggle='modal']").addEventListener("click", function () {
    console.log("Open button clicked");
    tempTask = null; // Reset temp task when opening the form
    document.getElementById("taskForm").reset();
    clearError(); // Clear any previous error message
});

// Close button event listener for the modal
document.querySelector(".btn-close").addEventListener("click", function () {
    console.log("Close button clicked");

    if (tempTask) {
        console.log("Restoring canceled task");
        addTaskToList(tempTask.taskName, tempTask.assignedDate, tempTask.dueDate);
        tempTask = null; // Clear temporary task
    }

    document.getElementById("taskForm").reset();
    clearError(); // Clear error message if any
});

// Handle Form Submission and Add Task to List
document.getElementById("taskForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent page reload

    // Get form data
    const taskName = document.getElementById("task_name").value;
    const assignedDate = document.getElementById("assigned_date").value;
    const dueDate = document.getElementById("due_date").value;

    // Validate dates
    if (!validateDates(assignedDate, dueDate)) {
        return; // Stop submission if validation fails
    }

    // If we're editing an existing task, update it; otherwise, add new task
    if (tempTask) {
        updateTaskInList(tempTask, taskName, assignedDate, dueDate);
    } else {
        addTaskToList(taskName, assignedDate, dueDate);
    }

    // Clear form inputs and close the modal via data-bs-dismiss
    document.getElementById("taskForm").reset();
    document.querySelector(".btn-close").click(); // Simulate click on close button
    tempTask = null; // Clear the temporary task since the form was submitted
    clearError(); // Clear error message if any
});

// Function to add a task to the list
function addTaskToList(taskName, assignedDate, dueDate) {
    const taskList = document.querySelector('.list-group');
    const newTask = document.createElement('a');
    newTask.classList.add('list-group-item', 'list-group-item-action');
    newTask.innerHTML = `
        <div class="d-flex w-100 justify-content-between">
            <strong class="mb-1">${taskName}</strong>
            <small>Due: ${dueDate}</small>
        </div>
        <p class="mb-1">Assigned: ${assignedDate}</p>
        <div class="task-actions d-flex justify-content-end gap-2">
            <button class="btn btn-sm btn-outline-secondary" onclick="editTask(this)">Edit</button>
            <button class="btn btn-sm btn-outline-danger" onclick="deleteTask(this)">Delete</button>
        </div>
    `;
    taskList.appendChild(newTask);
}

// Function to edit a task
function editTask(button) {
    const taskElement = button.closest('.list-group-item');
    const taskName = taskElement.querySelector('strong').textContent;
    const assignedDate = taskElement.querySelector('.mb-1').textContent.split('Assigned: ')[1];
    const dueDate = taskElement.querySelector('small').textContent.split('Due: ')[1];

    // Store task data for potential restoration or modification
    tempTask = { taskName, assignedDate, dueDate };

    // Populate form with task data
    document.getElementById("task_name").value = taskName;
    document.getElementById("assigned_date").value = assignedDate;
    document.getElementById("due_date").value = dueDate;

    // Open modal via the data-bs-toggle method
    document.querySelector("[data-bs-toggle='modal']").click();
}

// Function to delete a task
function deleteTask(button) {
    // Store the task element to be deleted
    const taskElement = button.closest('.list-group-item');

    // Store the task name for confirmation
    const taskName = taskElement.querySelector('strong').textContent;

    // Set the task name in the modal confirmation text
    document.getElementById('deleteTaskName').textContent = taskName;

    // Store the task element in a global variable for deletion upon confirmation
    window.taskToDelete = taskElement;

    // Show the confirmation modal
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteTaskModal'));
    deleteModal.show();
}

function confirmDelete() {
    if (window.taskToDelete) {
        // Remove the task from the list
        window.taskToDelete.remove();
        window.taskToDelete = null;

        // Close the modal
        const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteTaskModal'));
        deleteModal.hide();
    }
}


// Function to clear error message
function clearError() {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.style.display = 'none';
    }
}

// Function to show error message
function showError(message) {
    let errorElement = document.getElementById('error-message');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.id = 'error-message';
        errorElement.style.color = 'red';
        errorElement.style.marginTop = '10px';
        document.getElementById('taskForm').prepend(errorElement);
    }
    errorElement.textContent = message;
    errorElement.style.display = 'block';
}

// Function to validate dates
function validateDates(assignedDate, dueDate) {
    const assigned = new Date(assignedDate);
    const due = new Date(dueDate);

    if (assigned > due) {
        showError("Assigned date cannot be after the due date.");
        return false;
    }
    if (due < assigned) {
        showError("Due date cannot be before the assigned date.");
        return false;
    }
    return true;
}

// Function to update an existing task in the list
function updateTaskInList(taskData, taskName, assignedDate, dueDate) {
    const taskList = document.querySelector('.list-group');
    const taskItems = taskList.querySelectorAll('.list-group-item');

    taskItems.forEach(item => {
        const currentTaskName = item.querySelector('strong').textContent;
        if (currentTaskName === taskData.taskName) {
            item.querySelector('strong').textContent = taskName;
            item.querySelector('.mb-1').textContent = `Assigned: ${assignedDate}`;
            item.querySelector('small').textContent = `Due: ${dueDate}`;
        }
    });
}
