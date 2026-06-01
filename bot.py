import os
import logging
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import db

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8764519514:AAETTL1ZmL3dgbhyQH19tnr6wotjLIT1xA4")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://timerushbot-production.up.railway.app")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()


def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Открыть приложение",
        web_app=types.WebAppInfo(url=WEBAPP_URL)
    )
    return builder.as_markup()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "⏳ Это *Time Rush* — твой персональный минималистичный помощник по управлению дедлайнами и задачами.\n\n"
        "• Я помогу тебе не проспать сдачу лабораторных и важных проектов.\n"
        "• Буду присылать автоматические напоминания *за неделю* и *за день* до дедлайна.\n\n"
        "Нажми на кнопку ниже, чтобы открыть панель управления задачами и запустить таймер Pomodoro! 👇"
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")


async def check_deadlines_job():
    logging.info("Проверка дедлайнов по расписанию...")
    now = datetime.now()

    rows = db.get_upcoming_deadlines()

    for row in rows:
        task_id, user_id, title, deadline_date_str, notified_week, notified_day = row

        try:
            deadline_dt = datetime.strptime(deadline_date_str, "%Y-%m-%d")
        except ValueError:
            continue

        time_left = deadline_dt - now

        if timedelta(days=6, hours=23) < time_left <= timedelta(days=7) and not notified_week:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=f"🚨 *Напоминание за неделю!*\nДо дедлайна по задаче «{title}» осталось 7 дней. Самое время распределить задачи по матрице Эйзенхауэра!",
                    parse_mode="Markdown"
                )
                db.mark_as_notified(task_id, "week")
            except Exception as e:
                logging.error(f"Ошибка отправки уведомления: {e}")

        elif timedelta(hours=23) < time_left <= timedelta(days=1) and not notified_day:
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=f"🔥 *Срочно! Дедлайн завтра!*\nСдача задачи «{title}» уже через 24 часа. Включай Pomodoro-таймер на 25 минут и за работу!",
                    parse_mode="Markdown"
                )
                db.mark_as_notified(task_id, "day")
            except Exception as e:
                logging.error(f"Ошибка отправки уведомления: {e}")


async def main():
    db.init_db()

    scheduler.add_job(check_deadlines_job, "interval", hours=1)
    scheduler.start()
    logging.info("Планировщик уведомлений успешно запущен.")

    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())