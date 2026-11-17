const API_URL = "/api/tasks";
let activeFilter = 'all';

const taskList = document.getElementById('taskList');
const taskForm = document.getElementById('taskForm');
const modalOverlay = document.getElementById('modalOverlay');

document.getElementById('openModalBtn').addEventListener('click', () => modalOverlay.style.display = 'flex');
document.getElementById('closeModalBtn').addEventListener('click', () => modalOverlay.style.display = 'none');

async function fetchTasks() {
    try {
        const response = await fetch(API_URL);
        const tasks = await response.json();
        renderTasks(tasks);
    } catch (error) {
        console.error("Ошибка синхронизации данных:", error);
    }
}

taskForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('taskTitle').value.trim();
    const subject = document.getElementById('taskSubject').value.trim();
    const priority = document.getElementById('taskPriority').value;
    const deadline = document.getElementById('taskDeadline').value;

    if(!title || !subject || !deadline) return;

    await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, subject, priority, deadline })
    });

    modalOverlay.style.display = 'none';
    taskForm.reset();
    fetchTasks();
});

window.toggleTask = async function(id) {
    await fetch(`${API_URL}/${id}/toggle`, { method: "PATCH" });
    fetchTasks();
};

window.deleteTask = async function(id) {
    await fetch(`${API_URL}/${id}`, { method: "DELETE" });
    fetchTasks();
};

function updateCounters(tasks) {
    const current = tasks.filter(t => !t.completed).length;
    const completed = tasks.filter(t => t.completed).length;
    document.getElementById('currentCount').textContent = current;
    document.getElementById('completedCount').textContent = completed;
}

function renderTasks(tasks) {
    taskList.innerHTML = '';
    updateCounters(tasks);

    let filtered = tasks;
    if (activeFilter === 'current') filtered = tasks.filter(t => !t.completed);
    if (activeFilter === 'completed') filtered = tasks.filter(t => t.completed);

    if (filtered.length === 0) {
        taskList.innerHTML = '<div style="text-align:center; color:#8c91a5; margin-top:50px; font-size:0.95rem;">Задач в этом разделе нет</div>';
        return;
    }

    const now = new Date();
    const prioLabels = { high: 'Высокий', medium: 'Средний', low: 'Низкий' };

    filtered.forEach(task => {
        const li = document.createElement('li');
        li.className = `task-card ${task.completed ? 'completed-status' : ''}`;

        if (!task.completed) {
            const hoursLeft = (new Date(task.deadline) - now) / (1000 * 60 * 60);
            if (hoursLeft < 0) li.classList.add('deadline-danger');
            else if (hoursLeft <= 24) li.classList.add('deadline-warning');
        }

        const formattedDate = new Date(task.deadline).toLocaleString('ru-RU', {
            day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
        });

        li.innerHTML = `
            <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} onclick="toggleTask(${task.id})">
            <div class="task-main-content">
                <div class="task-title">${escapeHTML(task.title)}</div>
                <div class="task-subject">${escapeHTML(task.subject)}</div>
                <div class="task-footer">
                    <span class="prio-tag prio-${task.priority}">${prioLabels[task.priority]}</span>
                    <span class="task-time-badge">${formattedDate}</span>
                </div>
            </div>
            <button class="del-btn" onclick="deleteTask(${task.id})">&times;</button>
        `;
        taskList.appendChild(li);
    });
}

function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag));
}

document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        activeFilter = e.target.getAttribute('data-filter');
        fetchTasks();
    });
});

setInterval(fetchTasks, 60000);
fetchTasks();
