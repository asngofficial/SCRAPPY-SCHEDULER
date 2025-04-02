const TaskManager = (() => {
  // Private variables
  let tempTask = null;
  let taskToDelete = null;
  
  // DOM Cache
  const dom = {
    taskForm: document.getElementById("taskForm"),
    addTaskModal: new bootstrap.Modal('#addTaskModal'),
    deleteModal: new bootstrap.Modal('#deleteTaskModal'),
    errorElement: document.getElementById('error-message'),
  };

  // Initialize
  function init() {
    bindEvents();
  }

  // Event Bindings
  function bindEvents() {
    // Add Task Button
    document.querySelectorAll("[data-bs-toggle='modal']").forEach(btn => {
      btn.addEventListener("click", resetForm);
    });

    // Form Submission
    dom.taskForm?.addEventListener("submit", handleSubmit);
    
    // Delete Confirmation
    document.getElementById("confirmDelete")?.addEventListener("click", confirmDelete);
  }

  // Form Handler
  async function handleSubmit(e) {
    e.preventDefault();
    const submitBtn = dom.taskForm.querySelector("button[type='submit']");
    
    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';
      
      const formData = new FormData(dom.taskForm);
      const response = await fetch(dom.taskForm.action, {
        method: "POST",
        body: formData,
      });

      if (response.redirected) {
        window.location.href = response.url;
      } else if (!response.ok) {
        const error = await response.json();
        showError(error.message);
      }
    } catch (error) {
      showError("Network error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Save Task";
    }
  }

  // Helpers
  function resetForm() {
    dom.taskForm.reset();
    dom.taskForm.action = dom.taskForm.dataset.defaultAction;
    clearError();
  }

  function showError(message) {
    if (dom.errorElement) dom.errorElement.textContent = message;
  }

  function clearError() {
    if (dom.errorElement) dom.errorElement.textContent = '';
  }

  // Public API
  return { init };
})();

// Start on load
document.addEventListener("DOMContentLoaded", TaskManager.init);