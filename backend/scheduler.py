import logging
import asyncio
from datetime import datetime

# pyrefly: ignore [missing-import]
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# pyrefly: ignore [missing-import]
from apscheduler.triggers.date import DateTrigger
# pyrefly: ignore [missing-import]
from apscheduler.triggers.cron import CronTrigger
# pyrefly: ignore [missing-import]
from apscheduler.triggers.interval import IntervalTrigger

from backend.database import db_manager
from backend.notifier import notifier_broker
from backend.mongo_schema import ReminderDB

logger = logging.getLogger("assistant.scheduler")


class ReminderScheduler:

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("APScheduler AsyncIOScheduler started successfully.")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("APScheduler AsyncIOScheduler shut down.")


    async def load_and_schedule_all(self):
        active_reminders = await db_manager.get_reminders(active_only=True)

        logger.info(f"Loading and scheduling {len(active_reminders)} active reminders...")

        for r in active_reminders:
            await self.schedule_reminder(r)


    async def schedule_reminder(self, reminder: ReminderDB):
        job_id = reminder.id
        next_run = datetime.fromisoformat(reminder.next_run_time)
        now = datetime.now()

        async def job_execution_wrapper():
            await self.execute_reminder_job(reminder.id)

        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        if reminder.is_recurring:
            trigger = None

            if reminder.recurrence_pattern == "hourly":
                trigger = IntervalTrigger(hours=1, start_date=next_run)

            elif reminder.recurrence_pattern == "daily":
                h, m = 9, 0
                if reminder.time_of_day:
                    h, m = map(int, reminder.time_of_day.split(":"))
                trigger = CronTrigger(hour=h, minute=m)

            elif reminder.recurrence_pattern and reminder.recurrence_pattern.startswith("every "):
                day_name = reminder.recurrence_pattern.replace("every ", "").strip().lower()
                days_short = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                days_full = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

                day_of_week = None
                if day_name in days_full:
                    day_of_week = days_short[days_full.index(day_name)]

                h, m = 9, 0
                if reminder.time_of_day:
                    h, m = map(int, reminder.time_of_day.split(":"))

                trigger = CronTrigger(day_of_week=day_of_week, hour=h, minute=m)

            if not trigger:
                trigger = DateTrigger(run_date=next_run)

            self.scheduler.add_job(
                job_execution_wrapper,
                trigger=trigger,
                id=job_id,
                replace_existing=True
            )

            logger.info(f"Scheduled recurring job '{reminder.task}' (ID: {job_id}) with pattern '{reminder.recurrence_pattern}' at next run: {reminder.next_run_time}")

        else:
            if next_run <= now:
                run_time = datetime.now()
                logger.info(f"One-time job '{reminder.task}' (ID: {job_id}) scheduled time has already passed. Scheduling immediate trigger.")
            else:
                run_time = next_run

            self.scheduler.add_job(
                job_execution_wrapper,
                trigger=DateTrigger(run_date=run_time),
                id=job_id,
                replace_existing=True
            )
            logger.info(f"Scheduled one-time job '{reminder.task}' (ID: {job_id}) at run time: {run_time.isoformat()}")


    async def cancel_reminder(self, reminder_id: str):
        if self.scheduler.get_job(reminder_id):
            self.scheduler.remove_job(reminder_id)
            logger.info(f"Cancelled scheduled job from pool (ID: {reminder_id})")


    async def execute_reminder_job(self, reminder_id: str):
        logger.info(f"Executing scheduled reminder job trigger. ID: {reminder_id}")
        reminder = await db_manager.get_reminder(reminder_id)
        if not reminder:
            logger.warning(f"Fired job ID {reminder_id} not found in database.")
            return

        if reminder.status != "active":
            logger.warning(f"Fired job ID {reminder_id} is in status '{reminder.status}'. Ignoring execution.")
            return

        await notifier_broker.broadcast_alert(reminder)

        if reminder.is_recurring:
            from backend.graph import intent_extractor
            next_run_iso = intent_extractor._calculate_next_run(reminder, datetime.now())
            await db_manager.update_reminder_status(reminder_id, "active", next_run_iso)

            updated_reminder = await db_manager.get_reminder(reminder_id)
            if updated_reminder:
                await self.schedule_reminder(updated_reminder)
        else:
            await db_manager.update_reminder_status(reminder_id, "completed")
            logger.info(f"Job ID {reminder_id} (one-time) marked as 'completed' in database.")

reminder_scheduler = ReminderScheduler()
