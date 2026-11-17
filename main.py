import json
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="IT.TEAM Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "tasks.json"

# Создаем структуру папок и пустую БД при старте
if not os.path.exists("static"):
    os.makedirs("static")

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

class Task(BaseModel):
    id: int = None
    title: str
    subject: str
    priority: str
    deadline: str
    completed: bool = False

def load_tasks():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_tasks(tasks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# Навигация между страницами
@app.get("/")
def get_index():
    return FileResponse("index.html")

@app.get("/calendar")
def get_calendar():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Календарь дедлайнов</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="phone-container">
            <header>
                <div class="team-title">it. team</div>
                <div class="main-nav">
                    <h1>Календарь</h1>
                </div>
            </header>
            <div style="text-align: center; color: #8c91a5; margin-top: 120px;">
                <span style="font-size: 4rem;">📅</span>
                <p style="margin-top: 20px; font-size: 1.1rem; font-weight: 500;">Раздел Календаря в разработке</p>
            </div>
            <nav class="bottom-nav">
                <button class="nav-item" onclick="location.href='/'"><span class="nav-icon">📋</span> Задачи</button>
                <button class="nav-item active" onclick="location.href='/calendar'"><span class="nav-icon">📅</span> Календарь</button>
                <button class="nav-item" onclick="location.href='/group'"><span class="nav-icon">👥</span> Группа</button>
            </nav>
        </div>
    </body>
    </html>
    """)

@app.get("/group")
def get_group():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Моя академическая группа</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="phone-container">
            <header>
                <div class="team-title">it. team</div>
                <div class="main-nav">
                    <h1>Состав группы</h1>
                </div>
            </header>
            <div style="text-align: center; color: #8c91a5; margin-top: 120px;">
                <span style="font-size: 4rem;">👥</span>
                <p style="margin-top: 20px; font-size: 1.1rem; font-weight: 500;">Раздел Группы в разработке</p>
            </div>
            <nav class="bottom-nav">
                <button class="nav-item" onclick="location.href='/'"><span class="nav-icon">📋</span> Задачи</button>
                <button class="nav-item" onclick="location.href='/calendar'"><span class="nav-icon">📅</span> Календарь</button>
                <button class="nav-item active" onclick="location.href='/group'"><span class="nav-icon">👥</span> Группа</button>
            </nav>
        </div>
    </body>
    </html>
    """)

# REST API
@app.get("/api/tasks")
def get_tasks():
    tasks = load_tasks()
    return sorted(tasks, key=lambda x: (x["completed"], datetime.fromisoformat(x["deadline"])))

@app.post("/api/tasks")
def create_task(task: Task):
    tasks = load_tasks()
    task_dict = task.dict()
    task_dict["id"] = int(datetime.utcnow().timestamp() * 1000)
    tasks.append(task_dict)
    save_tasks(tasks)
    return task_dict

@app.patch("/api/tasks/{task_id}/toggle")
def toggle_task(task_id: int):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            save_tasks(tasks)
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = load_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(tasks) == len(new_tasks):
        raise HTTPException(status_code=404, detail="Task not found")
    save_tasks(new_tasks)
    return {"status": "success"}

app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
