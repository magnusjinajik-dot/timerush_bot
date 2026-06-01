import sqlite3
from datetime import datetime

# Название файла, в котором будет храниться вся наша база данных
DB_NAME = "timerush.db"


def init_db():
    """
    Инициализация базы данных.
    Эта функция проверяет, существует ли файл базы данных и нужная таблица.
    Если таблицы нет, она её создает. Вызывается один раз при старте бота.
    """
    # Устанавливаем соединение с файлом БД
    conn = sqlite3.connect (DB_NAME)
    # Создаем курсор — инструмент для выполнения SQL-запросов
    cursor = conn.cursor ()

    # Создаем таблицу задач (tasks), если она еще не создана
    cursor.execute ('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный номер (ID) задачи
            user_id INTEGER NOT NULL,            -- ID пользователя в Telegram, чтобы разделять задачи
            title TEXT NOT NULL,                 -- Название задачи/дедлайна 
            deadline_date TEXT NOT NULL,         -- Дата дедлайна в формате YYYY-MM-DD 
            priority TEXT NOT NULL,              -- Сектор матрицы Эйзенхауэра (например, 'urgent_important') 
            status TEXT DEFAULT 'active',        -- Статус задачи: 'active' (активна) или 'completed' (выполнена) 
            notified_week INTEGER DEFAULT 0,    -- Флаг: отправлено ли уведомление за 1 неделю (0 - нет, 1 - да) 
            notified_day INTEGER DEFAULT 0       -- Флаг: отправлено ли уведомление за 1 день (0 - нет, 1 - да) 
        )
    ''')

    # Сохраняем изменения в файле
    conn.commit ()
    # Закрываем соединение, чтобы освободить ресурсы
    conn.close ()


def add_task(user_id: int, title: str, deadline_date: str, priority: str):
    """
    Добавление новой задачи в базу данных[cite: 6].
    Принимает:
        user_id — Telegram ID пользователя
        title — Текст задачи
        deadline_date — Строка с датой (YYYY-MM-DD)
        priority — Строка с приоритетом (один из 4 секторов матрицы)
    """
    conn = sqlite3.connect (DB_NAME)
    cursor = conn.cursor ()

    # Запрос с использованием плейсхолдеров (?) для защиты от SQL-инъекций
    cursor.execute (
        """
        INSERT INTO tasks (user_id, title, deadline_date, priority) 
        VALUES (?, ?, ?, ?)
        """,
        (user_id, title, deadline_date, priority)
    )

    conn.commit ()
    conn.close ()


def get_user_tasks(user_id: int):
    """
    Получение списка всех активных задач конкретного пользователя[cite: 6].
    Возвращает список словарей, отсортированных по дате дедлайна.
    """
    conn = sqlite3.connect (DB_NAME)
    cursor = conn.cursor ()

    # Выбираем только те задачи, которые относятся к текущему пользователю и еще не выполнены
    cursor.execute (
        """
        SELECT id, title, deadline_date, priority, status 
        FROM tasks 
        WHERE user_id = ? AND status = 'active' 
        ORDER BY deadline_date ASC
        """,
        (user_id,)
    )

    rows = cursor.fetchall ()
    conn.close ()

    # Преобразуем кортежи из БД в удобный формат списка словарей для фронтенда
    tasks = []
    for row in rows:
        tasks.append ({
            "id": row[0],
            "title": row[1],
            "date": row[2],
            "priority": row[3],
            "status": row[4]
        })
    return tasks


def update_task_status(task_id: int, status: str):
    """
    Обновление статуса задачи (например, перевод в статус 'completed' при выполнении)[cite: 6, 83].
    """
    conn = sqlite3.connect (DB_NAME)
    cursor = conn.cursor ()

    cursor.execute (
        "UPDATE tasks SET status = ? WHERE id = ?",
        (status, task_id)
    )

    conn.commit ()
    conn.close ()


def delete_task(task_id: int):
    """
    Полное удаление задачи из базы данных по её уникальному ID[cite: 6].
    """
    conn = sqlite3.connect (DB_NAME)
    cursor = conn.cursor ()

    cursor.execute (
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit ()
    conn.close ()


def get_upcoming_deadlines():
    """
    Функция для планировщика уведомлений (бэкенда бота)[cite: 7].
    Выбирает абсолютно все активные задачи всех пользователей,
    чтобы бот мог проверить, кому пора отправлять пуш.
    """
    conn = sqlite3.connect (DB_NAME)
    cursor = conn.cursor ()

    cursor.execute (
        """
        SELECT id, user_id, title, deadline_date, notified_week, notified_day 
        FROM tasks 
        WHERE status = 'active'
        """
    )

    rows = cursor.fetchall ()
    conn.close ()
    return rows


def mark_as_notified(task_id: int, period_type: str):
    """
    Отметка в базе данных о том, что уведомление по задаче уже было отправлено.
    Это предотвращает повторную отправку одного и того же напоминания каждый час.
    period_type может быть 'week' или 'day'.
    """
    conn = sqlite3.connect (DB_NAME)
    cursor = conn.cursor ()

    if period_type == "week":
        cursor.execute ("UPDATE tasks SET notified_week = 1 WHERE id = ?", (task_id,))
    elif period_type == "day":
        cursor.execute ("UPDATE tasks SET notified_day = 1 WHERE id = ?", (task_id,))

    conn.commit ()
    conn.close ()