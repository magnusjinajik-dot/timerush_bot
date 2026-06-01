import sqlite3
from datetime import datetime

DB_NAME = "timerush.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            deadline_date TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            notified_week INTEGER DEFAULT 0,
            notified_day INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


def add_task(user_id: int, title: str, deadline_date: str, priority: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_id, title, deadline_date, priority) VALUES (?, ?, ?, ?)",
        (user_id, title, deadline_date, priority)
    )
    conn.commit()
    conn.close()


def get_user_tasks(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, deadline_date, priority, status
        FROM tasks
        WHERE user_id = ? AND status = 'active'
        ORDER BY deadline_date ASC
        """,
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "date": row[2],      # фронтенд ждёт поле "date"
            "priority": row[3],
            "status": row[4]
        })
    return tasks


def update_task_status(task_id: int, status: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()


def delete_task(task_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def get_upcoming_deadlines():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, user_id, title, deadline_date, notified_week, notified_day
        FROM tasks
        WHERE status = 'active'
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def mark_as_notified(task_id: int, period_type: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if period_type == "week":
        cursor.execute("UPDATE tasks SET notified_week = 1 WHERE id = ?", (task_id,))
    elif period_type == "day":
        cursor.execute("UPDATE tasks SET notified_day = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()