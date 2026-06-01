from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import db

app = FastAPI()

app.mount("/", StaticFiles(directory=".", html=True), name="static")

class TaskIn(BaseModel):
    user_id: int
    title: str
    date: str
    priority: str

class TaskId(BaseModel):
    task_id: int

@app.get("/api/tasks")
def get_tasks(user_id: int):
    tasks = db.get_user_tasks(user_id)
    return JSONResponse({"tasks": tasks})

@app.post("/api/tasks/add")
def add_task(task: TaskIn):
    db.add_task(task.user_id, task.title, task.date, task.priority)
    return {"ok": True}

@app.post("/api/tasks/complete")
def complete_task(data: TaskId):
    db.update_task_status(data.task_id, "completed")
    return {"ok": True}

@app.post("/api/tasks/delete")
def delete_task(data: TaskId):
    db.delete_task(data.task_id)
    return {"ok": True}