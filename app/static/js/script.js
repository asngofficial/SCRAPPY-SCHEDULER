const TaskManager = (() => {
    // Private variables
    let tempTask = null;
    let taskToDelete = null;

    // DOM Cache
    const dom = {
        taskForm: document.getElementById("taskForm"),
        addTaskModal: document.getElementById('addTaskModal') ? new bootstrap.Modal('#addTaskModal') : null,
        deleteModal: document.getElementById('deleteTaskModal') ? new bootstrap.Modal('#deleteTaskModal') : null,
        errorElement: document.getElementById('error-message'),
        csrfToken: document.querySelector('input[name="csrf_token"]')
    };

    // Initialize
    function init() {
        if (!dom.taskForm) {
            console.error('Task form not found');
            return;
        }
        bindEvents();
        setDefaultDates();
    }

    // Event Bindings
    function bindEvents() {
        // Add Task Button
        document.querySelectorAll("[data-bs-target='#addTaskModal']").forEach(btn => {
            btn.addEventListener("click", resetForm);
        });

        // Form Submission
        dom.taskForm.addEventListener("submit", handleSubmit);

        // Delete Confirmation
        document.getElementById("confirmDelete")?.addEventListener("click", confirmDelete);

        // Modal show event for setting default dates
        if (dom.addTaskModal) {
            document.getElementById('addTaskModal').addEventListener('show.bs.modal', setDefaultDates);
        }
    }

    // Form Handler
    async function handleSubmit(e) {
        e.preventDefault();
        const submitBtn = dom.taskForm.querySelector("button[type='submit']");

        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';

            const formData = new FormData(dom.taskForm);

            // Add CSRF token if not already in form
            if (dom.csrfToken && !formData.has('csrf_token')) {
                formData.append('csrf_token', dom.csrfToken.value);
            }

            const response = await fetch(dom.taskForm.action, {
                method: "POST",
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                if (dom.addTaskModal) dom.addTaskModal.hide();
                window.location.reload();
            } else {
                showError(data.message || "Failed to save task");
                console.error('Server error:', data);
            }
        } catch (error) {
            showError("Network error - please try again");
            console.error('Fetch error:', error);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Save Task";
        }
    }

    // Set default dates in form
    function setDefaultDates() {
        if (!dom.taskForm || dom.taskForm.querySelector('input[name="task_id"]').value) return;

        const now = new Date();
        const timezoneOffset = now.getTimezoneOffset() * 60000;
        const localISOTime = (new Date(now - timezoneOffset)).toISOString().slice(0, 16);

        const startDate = dom.taskForm.querySelector('input[name="start_date"]');
        const dueDate = dom.taskForm.querySelector('input[name="due_date"]');

        if (startDate && !startDate.value) startDate.value = localISOTime;
        if (dueDate && !dueDate.value) dueDate.value = localISOTime;
    }

    // Helpers
    function resetForm() {
        if (!dom.taskForm) return;

        dom.taskForm.reset();
        if (dom.taskForm.dataset.defaultAction) {
            dom.taskForm.action = dom.taskForm.dataset.defaultAction;
        }
        clearError();
        setDefaultDates();
    }

    function showError(message) {
        if (!dom.errorElement) {
            console.error('Error:', message);
            return;
        }
        dom.errorElement.textContent = message;
        dom.errorElement.classList.remove('d-none');

        // Auto-hide error after 5 seconds
        setTimeout(clearError, 5000);
    }

    function clearError() {
        if (dom.errorElement) {
            dom.errorElement.textContent = '';
            dom.errorElement.classList.add('d-none');
        }
    }

    // Delete confirmation handler
    async function confirmDelete() {
        if (!taskToDelete) return;

        try {
            const response = await fetch(`/delete-task/${taskToDelete}`, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': dom.csrfToken?.value || ''
                }
            });

            if (response.ok) {
                window.location.reload();
            } else {
                throw new Error('Delete failed');
            }
        } catch (error) {
            showError("Failed to delete task");
            console.error('Delete error:', error);
        }
    }

    // Public API
    return {
        init,
        setTaskToDelete: (id) => { taskToDelete = id; }
    };
})();

// Start on load
document.addEventListener("DOMContentLoaded", () => {
    // Check if Bootstrap Modal exists before initializing
    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        TaskManager.init();
    } else {
        console.error('Bootstrap Modal not loaded');
    }
});