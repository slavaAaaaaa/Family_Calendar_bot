from aiogram import Router, F, Bot, exceptions
from aiogram.types import Message, CallbackQuery
from apscheduler.triggers.date import DateTrigger

from database import Database
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from logging.handlers import RotatingFileHandler
from token_bot import Token

import asyncio
import logging
import pendulum

notif_router = Router()
db = Database()
bot = Bot(token=Token)

# Initialize scheduler but don't start it here
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler("bot.log", maxBytes=5*1024*1024, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@notif_router.startup()
async def start_scheduler():
    """Start the scheduler when the bot starts"""
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


@notif_router.shutdown()
async def shutdown_scheduler():
    """Shutdown the scheduler when the bot stops"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down")


@notif_router.callback_query(F.data == "create_notif")
async def create_notif(callback: CallbackQuery):
    user_id = callback.from_user.id
    logger.info(f"User {user_id} requested notifications creation")

    try:
        notif_date = db.get_user_events(user_id=user_id)
        logger.debug(f"Retrieved events for user {user_id}: {notif_date}")

        if not notif_date:
            logger.info(f"No events found for user {user_id}")
            await callback.message.answer("❌ Нет событий для создания уведомлений.")
            return

        created_notifications = []

        for event in notif_date:
            try:
                run_dt = pendulum.parse(f"{event['date']} {event['time']}", tz="Europe/Moscow")
                logger.debug(f"Parsed datetime for event {event['name']}: {run_dt}")

                if run_dt < pendulum.now():
                    logger.warning(f"Event {event['name']} is in the past, skipping")
                    continue

                scheduler.add_job(
                    send_notification,
                    trigger=DateTrigger(run_date=run_dt),
                    kwargs={
                        "user_id": user_id,
                        "event_name": event["name"],
                        "event_time": event["time"],
                        "event_desc": event.get("description", "Нет описания")
                    }
                )
                logger.info(f"Scheduled notification for event {event['name']} at {run_dt}")
                created_notifications.append(
                    f"Уведомление о событии '{event['name']}' запланировано на {run_dt.to_datetime_string()}.")
            except Exception as e:
                logger.error(f"Error scheduling event {event}: {str(e)}", exc_info=True)
                continue

        if created_notifications:
            msg = "✅ Уведомления созданы:\n" + "\n".join(created_notifications)
            logger.info(f"Successfully created notifications for user {user_id}")
            await callback.message.answer(msg)

        else:
            msg = "❌ Не удалось создать ни одного уведомления (возможно, все события в прошлом)."
            logger.warning(msg)
            await callback.message.answer(msg)

    except Exception as e:
        logger.critical(f"Unexpected error in create_notif: {str(e)}", exc_info=True)
        await callback.message.answer("⚠ Произошла ошибка при создании уведомлений")


async def send_notification(user_id: int, event_name: str, event_time: str, event_desc: str):
    try:
        text = (
            f"🔔 Напоминание о событии!\n\n"
            f"{event_name}\n"
            f"{event_desc}\n"
            f"🕒 Время: {event_time}"
        )
        await bot.send_message(chat_id=user_id, text=text)
        logger.info(f"Notification sent to user {user_id} about event {event_name}")
    except exceptions.BotBlocked:
        logger.warning(f"User {user_id} blocked the bot")
    except exceptions.ChatNotFound:
        logger.warning(f"Chat with user {user_id} not found")
    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {str(e)}", exc_info=True)


@notif_router.message(F.text == "/jobs")
async def show_jobs(message: Message):
    jobs = scheduler.get_jobs()
    if not jobs:
        await message.answer("Нет активных уведомлений")
        return

    response = ["Активные уведомления:"]
    for job in jobs:
        response.append(f"- {job.id}: {job.kwargs['event_name']} в {job.next_run_time}")

    await message.answer("\n".join(response))


@notif_router.callback_query(F.data == "cancel_notif")
async def cancel_notif(message: Message):
    await message.answer("Сделано. Для удаления события введите /delete_events, а для просомтра всех - /show_events")
