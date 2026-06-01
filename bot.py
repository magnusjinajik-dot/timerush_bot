import os
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Включаем логирование
logging.basicConfig (level=logging.INFO)

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8764519514:AAETTL1ZmL3dgbhyQH19tnr6wotjLIT1xA4"  # Ваш токен от BotFather

# Сюда мы вставим ссылку, которую нам выдаст Pinggy (Шаг 2)
WEBAPP_URL = "https://timerush-production.up.railway.app"

bot = Bot (token=BOT_TOKEN)
dp = Dispatcher ()
scheduler = AsyncIOScheduler ()

# Имитация базы данных дедлайнов (для примера)
# В реальном проекте здесь будет запрос к вашей БД
DB_DEADLINES_MOCK = [
    {"user_id": None, "title": "Лабораторная по физике", "date": datetime.now () + timedelta (days=7)},
    {"user_id": None, "title": "Отчет по сетям (DNS)", "date": datetime.now () + timedelta (days=1)}
]


# --- КНОПКА MINI APP ---
def get_main_keyboard():
    builder = InlineKeyboardBuilder ()
    # Создаем кнопку типа WebApp, которая откроет Mini App и на ПК, и на телефоне
    builder.button (
        text="🚀 Открыть приложение",
        web_app=types.WebAppInfo (url=WEBAPP_URL)
    )
    return builder.as_markup ()


# --- ОБРАБОТЧИК КОМАНДЫ /START ---
@dp.message (Command ("start"))
async def cmd_start(message: types.Message):
    # Привязываем ID пользователя к нашей тестовой базе данных
    for deadline in DB_DEADLINES_MOCK:
        deadline["user_id"] = message.from_user.id

    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "⏳ Это **Time Rush** — твой персональный минималистичный помощник по управлению дедлайнами и задачами.\n\n"
        "• Я помогу тебе не проспать сдачу лабораторных и важных проектов.\n"
        "• Буду присылать автоматические напоминания **за неделю** и **за день** до дедлайна.\n\n"
        "Нажми на кнопку ниже, чтобы открыть панель управления задачами и запустить таймер Pomodoro! 👇"
    )

    await message.answer (welcome_text, reply_markup=get_main_keyboard (), parse_mode="Markdown")


# --- ФУНКЦИЯ ПРОВЕРКИ ДЕДЛАЙНОВ (ПЛАНИРОВЩИК) ---
async def check_deadlines_job():
    logging.info ("Проверка дедлайнов по расписанию...")
    now = datetime.now ()

    for deadline in DB_DEADLINES_MOCK:
        if not deadline["user_id"]:
            continue

        time_left = deadline["date"] - now

        # Проверяем дедлайн за 7 дней (с погрешностью в пределах часа запуска задачи)
        if timedelta (days=6, hours=23) < time_left <= timedelta (days=7):
            await bot.send_message (
                chat_id=deadline["user_id"],
                text=f"🚨 **Напоминание за неделю!**\nДо дедлайна по задаче «{deadline['title']}» осталось 7 дней. Самое время распределить задачи по матрице Эйзенхауэра!"
            )

        # Проверяем дедлайн за 1 день
        elif timedelta (hours=23) < time_left <= timedelta (days=1):
            await bot.send_message (
                chat_id=deadline["user_id"],
                text=f"🔥 **Срочно! Дедлайн завтра!**\nСдача задачи «{deadline['title']}» уже через 24 часа. Включай Pomodoro-таймер на 25 минут и за работу!"
            )


# --- ЗАПУСК БОТА ---
async def main():
    # Настраиваем планировщик на запуск проверки каждый час
    scheduler.add_job (check_deadlines_job, "interval", hours=1)
    scheduler.start ()
    logging.info ("Планировщик уведомлений успешно запущен.")

    # Запускаем получение обновлений от Telegram
    await dp.start_polling (bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run (main ())