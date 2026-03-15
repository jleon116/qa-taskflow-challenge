/**
 * TaskFlow — Frontend Application
 * Contains intentional bugs for QA assessment
 */

const API = "/api";
let currentPage = 1;
let currentFilters = {};

// ─── Init ────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    loadStats();
    loadTasks();
    loadProjects();
    loadUsers();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById("btn-new-task").addEventListener("click", openNewTaskModal);
    document.getElementById("btn-close-modal").addEventListener("click", closeModal);
    document.getElementById("btn-cancel").addEventListener("click", closeModal);
    document.getElementById("btn-close-detail").addEventListener("click", closeDetail);
    document.getElementById("btn-export").addEventListener("click", exportTasks);
    document.getElementById("task-form").addEventListener("submit", handleTaskSubmit);

    // Filters
    document.getElementById("filter-project").addEventListener("change", applyFilters);
    document.getElementById("filter-status").addEventListener("change", applyFilters);
    document.getElementById("filter-priority").addEventListener("change", applyFilters);

    // 🐛 UI BUG: Search input has no debounce — fires on every keystroke
    // causing excessive API calls
    document.getElementById("filter-search").addEventListener("input", applyFilters);

    // Close modal on overlay click
    document.getElementById("modal-overlay").addEventListener("click", (e) => {
        if (e.target.id === "modal-overlay") closeModal();
    });
    document.getElementById("detail-overlay").addEventListener("click", (e) => {
        if (e.target.id === "detail-overlay") closeDetail();
    });
}

// ─── API Calls ───────────────────────────────────────────
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API}${endpoint}`, {
            headers: { "Content-Type": "application/json" },
            ...options,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: "Unknown error" }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        return response.json();
    } catch (err) {
        console.error(`API Error: ${err.message}`);
        // 🐛 UI BUG: Error messages not shown to user — only logged to console
        throw err;
    }
}

// ─── Stats ───────────────────────────────────────────────
async function loadStats() {
    try {
        const stats = await apiCall("/stats");
        document.getElementById("stat-total").textContent = stats.total_tasks;
        document.getElementById("stat-todo").textContent = stats.by_status?.todo || 0;
        document.getElementById("stat-progress").textContent = stats.by_status?.in_progress || 0;
        document.getElementById("stat-done").textContent = stats.by_status?.done || 0;
        document.getElementById("stat-overdue").textContent = stats.overdue;
    } catch (err) {
        console.error("Failed to load stats");
    }
}

// ─── Tasks ───────────────────────────────────────────────
async function loadTasks() {
    const params = new URLSearchParams();
    params.set("page", currentPage);
    params.set("page_size", 15);

    if (currentFilters.project_id) params.set("project_id", currentFilters.project_id);
    if (currentFilters.status) params.set("status", currentFilters.status);
    if (currentFilters.priority) params.set("priority", currentFilters.priority);
    if (currentFilters.search) params.set("search", currentFilters.search);

    try {
        const data = await apiCall(`/tasks?${params.toString()}`);
        renderTasks(data.tasks);
        renderPagination(data.page, data.total_pages);
    } catch (err) {
        document.getElementById("task-list").innerHTML =
            '<p class="loading">Error al cargar tareas</p>';
    }
}

function renderTasks(tasks) {
    const container = document.getElementById("task-list");

    if (!tasks.length) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No hay tareas</p>
                <p style="font-size: 0.85rem">Crea una nueva tarea para comenzar</p>
            </div>`;
        return;
    }

    container.innerHTML = tasks.map(task => {
        const isDone = task.status === "done";
        const tags = (task.tags || []).map(t => `<span class="tag">${t}</span>`).join(" ");
        const dueClass = isOverdue(task.due_date, task.status) ? "overdue" : "";
        const dueText = task.due_date ? formatDate(task.due_date) : "";

        return `
        <div class="task-card priority-${task.priority} status-${task.status}"
             onclick="openTaskDetail('${task.id}')">
            <div class="task-checkbox ${isDone ? 'done' : ''}"
                 onclick="event.stopPropagation(); toggleDone('${task.id}', '${task.status}')">
                ${isDone ? '✓' : ''}
            </div>
            <div class="task-info">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-meta">
                    <span class="badge badge-${task.status}">${formatStatus(task.status)}</span>
                    ${tags}
                    ${dueText ? `<span class="due-date ${dueClass}">📅 ${dueText}</span>` : ''}
                </div>
            </div>
            <div class="task-actions">
                <button class="btn btn-sm btn-secondary"
                        onclick="event.stopPropagation(); editTask('${task.id}')">✏️</button>
                <button class="btn btn-sm btn-danger"
                        onclick="event.stopPropagation(); deleteTask('${task.id}')">🗑️</button>
            </div>
        </div>`;
    }).join("");
}

function renderPagination(current, total) {
    const container = document.getElementById("pagination");
    if (total <= 1) { container.innerHTML = ""; return; }

    let html = "";
    for (let i = 1; i <= total; i++) {
        html += `<button class="page-btn ${i === current ? 'active' : ''}"
                         onclick="goToPage(${i})">${i}</button>`;
    }
    container.innerHTML = html;
}

// ─── Task Actions ────────────────────────────────────────
async function toggleDone(taskId, currentStatus) {
    const newStatus = currentStatus === "done" ? "todo" : "done";
    try {
        await apiCall(`/tasks/${taskId}`, {
            method: "PUT",
            body: JSON.stringify({ status: newStatus }),
        });
        loadTasks();
        loadStats();
    } catch (err) {
        alert("Error al actualizar tarea");
    }
}

async function deleteTask(taskId) {
    // 🐛 UI BUG: No confirmation dialog before deleting
    try {
        await apiCall(`/tasks/${taskId}`, { method: "DELETE" });
        loadTasks();
        loadStats();
    } catch (err) {
        alert("Error al eliminar tarea");
    }
}

async function editTask(taskId) {
    // 🐛 UI BUG: Edit opens the same "new task" form but doesn't pre-populate fields
    openNewTaskModal();
}

// ─── Task Detail ─────────────────────────────────────────
async function openTaskDetail(taskId) {
    try {
        const task = await apiCall(`/tasks/${taskId}`);
        const comments = await apiCall(`/tasks/${taskId}/comments`);

        const content = document.getElementById("detail-content");
        content.innerHTML = `
            <div class="detail-row">
                <div class="detail-field">
                    <div class="detail-label">Estado</div>
                    <div class="detail-value">
                        <select onchange="updateTaskStatus('${task.id}', this.value)">
                            <option value="todo" ${task.status === 'todo' ? 'selected' : ''}>Por Hacer</option>
                            <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>En Progreso</option>
                            <option value="in_review" ${task.status === 'in_review' ? 'selected' : ''}>En Revisión</option>
                            <option value="done" ${task.status === 'done' ? 'selected' : ''}>Completada</option>
                            <option value="cancelled" ${task.status === 'cancelled' ? 'selected' : ''}>Cancelada</option>
                        </select>
                    </div>
                </div>
                <div class="detail-field">
                    <div class="detail-label">Prioridad</div>
                    <div class="detail-value"><span class="badge badge-${task.priority}">${task.priority}</span></div>
                </div>
            </div>
            <div class="detail-field">
                <div class="detail-label">Descripción</div>
                <div class="detail-value">${task.description || '<em style="color:#94a3b8">Sin descripción</em>'}</div>
            </div>
            <div class="detail-row">
                <div class="detail-field">
                    <div class="detail-label">Fecha límite</div>
                    <div class="detail-value">${task.due_date || 'No definida'}</div>
                </div>
                <div class="detail-field">
                    <div class="detail-label">Creada</div>
                    <div class="detail-value">${formatDateTime(task.created_at)}</div>
                </div>
            </div>
            ${task.tags && task.tags.length ? `
                <div class="detail-field">
                    <div class="detail-label">Etiquetas</div>
                    <div class="detail-value">${task.tags.map(t => `<span class="tag">${t}</span>`).join(' ')}</div>
                </div>
            ` : ''}
            <div class="comments-section">
                <h3 style="font-size:0.95rem;margin-bottom:12px">Comentarios (${comments.total})</h3>
                ${comments.comments.map(c => `
                    <div class="comment-item">
                        <div class="comment-meta">${c.author_id} · ${formatDateTime(c.created_at)}</div>
                        <div class="comment-text">${escapeHtml(c.content)}</div>
                    </div>
                `).join("") || '<p style="color:#94a3b8;font-size:0.85rem">Sin comentarios</p>'}
                <div class="comment-input">
                    <input type="text" id="new-comment" placeholder="Agregar comentario...">
                    <button class="btn btn-primary btn-sm"
                            onclick="addComment('${task.id}')">Enviar</button>
                </div>
            </div>`;

        document.getElementById("detail-title").textContent = task.title;
        document.getElementById("detail-overlay").classList.add("active");
    } catch (err) {
        alert("Error al cargar detalle de tarea");
    }
}

async function updateTaskStatus(taskId, newStatus) {
    try {
        await apiCall(`/tasks/${taskId}`, {
            method: "PUT",
            body: JSON.stringify({ status: newStatus }),
        });
        loadTasks();
        loadStats();
    } catch (err) {
        alert("Error al actualizar estado");
    }
}

async function addComment(taskId) {
    const input = document.getElementById("new-comment");
    const content = input.value.trim();
    if (!content) return;

    try {
        // 🐛 UI BUG: Hardcoded author_id — should come from logged-in user
        await apiCall(`/tasks/${taskId}/comments`, {
            method: "POST",
            body: JSON.stringify({
                task_id: taskId,
                author_id: "system",
                content: content,
            }),
        });
        input.value = "";
        openTaskDetail(taskId); // Refresh
    } catch (err) {
        alert("Error al agregar comentario");
    }
}

// ─── Filters ─────────────────────────────────────────────
function applyFilters() {
    currentFilters = {
        project_id: document.getElementById("filter-project").value,
        status: document.getElementById("filter-status").value,
        priority: document.getElementById("filter-priority").value,
        search: document.getElementById("filter-search").value,
    };
    currentPage = 1;
    loadTasks();
    // 🐛 UI BUG: Stats don't update when filters change
    // loadStats() should be called with project filter
}

function goToPage(page) {
    currentPage = page;
    loadTasks();
    window.scrollTo({ top: 0, behavior: "smooth" });
}

// ─── Modal ───────────────────────────────────────────────
function openNewTaskModal() {
    document.getElementById("task-form").reset();
    document.getElementById("modal-title").textContent = "Nueva Tarea";
    document.getElementById("modal-overlay").classList.add("active");
}

function closeModal() {
    document.getElementById("modal-overlay").classList.remove("active");
}

function closeDetail() {
    document.getElementById("detail-overlay").classList.remove("active");
}

async function handleTaskSubmit(e) {
    e.preventDefault();

    const tagsInput = document.getElementById("task-tags").value;
    const tags = tagsInput ? tagsInput.split(",").map(t => t.trim()).filter(Boolean) : [];

    const payload = {
        title: document.getElementById("task-title").value.trim(),
        description: document.getElementById("task-description").value.trim() || null,
        project_id: document.getElementById("task-project").value,
        assignee_id: document.getElementById("task-assignee").value || null,
        reporter_id: "system", // 🐛 UI BUG: Hardcoded reporter
        priority: document.getElementById("task-priority").value,
        due_date: document.getElementById("task-due-date").value || null,
        tags: tags,
    };

    // 🐛 UI BUG: No client-side validation — empty title with spaces passes
    if (!payload.title) {
        alert("El título es requerido");
        return;
    }

    try {
        await apiCall("/tasks", {
            method: "POST",
            body: JSON.stringify(payload),
        });
        closeModal();
        loadTasks();
        loadStats();
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

// ─── Export ──────────────────────────────────────────────
async function exportTasks() {
    // 🐛 UI BUG: Export always exports ALL tasks, ignoring current filters
    try {
        const data = await apiCall("/export/tasks?format=csv");
        const blob = new Blob([data], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "tasks_export.csv";
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        alert("Error al exportar");
    }
}

// ─── Data Loaders ────────────────────────────────────────
async function loadProjects() {
    try {
        const data = await apiCall("/projects");
        const selects = [
            document.getElementById("filter-project"),
            document.getElementById("task-project"),
        ];
        data.projects.forEach(p => {
            selects.forEach(sel => {
                const opt = document.createElement("option");
                opt.value = p.id;
                opt.textContent = p.name;
                sel.appendChild(opt);
            });
        });
    } catch (err) {
        console.error("Failed to load projects");
    }
}

async function loadUsers() {
    try {
        const data = await apiCall("/users");
        const select = document.getElementById("task-assignee");
        data.users.forEach(u => {
            const opt = document.createElement("option");
            opt.value = u.id;
            opt.textContent = u.full_name;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error("Failed to load users");
    }
}

// ─── Helpers ─────────────────────────────────────────────
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function formatStatus(status) {
    const map = {
        todo: "Por Hacer", in_progress: "En Progreso",
        in_review: "En Revisión", done: "Completada", cancelled: "Cancelada",
    };
    return map[status] || status;
}

function formatDate(dateStr) {
    if (!dateStr) return "";
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString("es-CO", { day: "numeric", month: "short" });
    } catch {
        return dateStr;
    }
}

function formatDateTime(dateStr) {
    if (!dateStr) return "";
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString("es-CO", {
            day: "numeric", month: "short", year: "numeric",
            hour: "2-digit", minute: "2-digit",
        });
    } catch {
        return dateStr;
    }
}

function isOverdue(dueDate, status) {
    if (!dueDate || status === "done" || status === "cancelled") return false;
    return new Date(dueDate) < new Date();
}
