import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime

from backend.config import settings
from backend.mongo_schema import ReminderDB


logger = logging.getLogger("assistanlifecyclet.notifier")


class NotifierBroker:

    def __init__(self):
        self._sse_queues: List[asyncio.Queue] = []


    async def register_client(self) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._sse_queues.append(queue)
        logger.info(f"SSE client registered. Total active listeners: {len(self._sse_queues)}")
        return queue


    def unregister_client(self, queue: asyncio.Queue):
        if queue in self._sse_queues:
            self._sse_queues.remove(queue)
            logger.info(f"SSE client disconnected. Total active listeners: {len(self._sse_queues)}")


    async def broadcast_alert(self, reminder: ReminderDB):
        alert_payload = {
            "event": "reminder_trigger",
            "id": reminder.id,
            "task": reminder.task,
            "priority": reminder.priority,
            "timestamp": datetime.now().isoformat(),
            "original_text": reminder.original_text
        }

        logger.info(f"Broadcasting notification alert for task: '{reminder.task}' to all SSE clients.")

        for q in self._sse_queues:
            await q.put(alert_payload)

        await self._send_telegram_notification(reminder)


    async def _send_telegram_notification(self, reminder: ReminderDB):
        token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID

        if not token or not chat_id:
            logger.info("Telegram Bot credentials not fully configured. Skipping Telegram notification.")
            return

        message_text = (
            f" <b>Personal Reminder</b>\n\n"
            f" <b>Task:</b> {reminder.task}\n"
            f" <b>Priority:</b> {reminder.priority.upper()}\n"
            f" <b>Scheduled Time:</b> {reminder.next_run_time}\n"
            f" <b>Recurring:</b> {'Yes (' + (reminder.recurrence_pattern or 'daily') + ')' if reminder.is_recurring else 'No'}\n\n"
            f" <i>Original command: \"{reminder.original_text}\"</i>"
        )

        loop = asyncio.get_event_loop()

        try:
            await loop.run_in_executor(None, self._telegram_send_sync, token, chat_id, message_text)
            logger.info(f"Telegram notification successfully sent to Chat ID {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")


    def _telegram_send_sync(self, token: str, chat_id: str, text: str):
        import requests

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }

        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()


notifier_broker = NotifierBroker()
