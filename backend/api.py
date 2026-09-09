import logging
import uuid
import json
import asyncio
from datetime import datetime
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, Request
# pyrefly: ignore [missing-import]
from fastapi.responses import StreamingResponse

from backend.config import settings
from backend.schemas import ReminderRequest
from backend.mongo_schema import ReminderDB
from backend.database import db_manager
from backend.scheduler import reminder_scheduler
from backend.graph import intent_extractor
from backend.notifier import notifier_broker

logger = logging.getLogger("assistant.api")

router = APIRouter(prefix="/api")


@router.post("/reminders", response_model=ReminderDB)
async def create_reminder(payload: ReminderRequest):

    try:
        now = datetime.now()
        intent = await intent_extractor.extract(payload.text, now)
        reminder_id = uuid.uuid4().hex[:12]
        
        reminder_record = ReminderDB(
            id=reminder_id,
            task=intent.task,
            priority=intent.priority,
            is_recurring=intent.is_recurring,
            recurrence_pattern=intent.recurrence_pattern,
            time_of_day=intent.time_of_day,
            date_str=intent.date_str,
            next_run_time=intent.extracted_datetime,
            created_at=now.isoformat(),
            status="active",
            original_text=payload.text
        )
        
        await db_manager.save_reminder(reminder_record)
    
        await reminder_scheduler.schedule_reminder(reminder_record)

        logger.info(f"Successfully processed and created reminder (ID: {reminder_id}) for task: '{reminder_record.task}'")
        return reminder_record

    except Exception as e:
        logger.exception("Failed to create reminder due to server error.")
        raise HTTPException(status_code=500, detail=f"Failed to process and schedule reminder: {str(e)}")


@router.get("/reminders")
async def list_reminders(active_only: bool = False):
    try:
        reminders = await db_manager.get_reminders(active_only=active_only)
        reminders.sort(key=lambda r: (r.status != "active", r.next_run_time))
        return reminders
    except Exception as e:
        logger.error(f"Error fetching reminders list: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reminders database.")


@router.delete("/reminders/{reminder_id}")
async def delete_reminder(reminder_id: str):
    try:
        await reminder_scheduler.cancel_reminder(reminder_id)
        deleted = await db_manager.delete_reminder(reminder_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Reminder ID not found in database.")
        logger.info(f"Deleted reminder ID {reminder_id} from database and scheduler.")
        return {"success": True, "message": f"Reminder {reminder_id} deleted successfully."}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete reminder: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while deleting reminder.")


@router.get("/stream")
async def sse_notification_stream(request: Request):
    client_queue = await notifier_broker.register_client()
    
    async def sse_event_generator():
        try:
            while True:
                try:
                    data = await asyncio.wait_for(client_queue.get(), timeout=15.0)
                    yield f"event: reminder_trigger\ndata: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield "event: keepalive\ndata: {}\n\n"
        except asyncio.CancelledError:
            logger.info("SSE connection closed by client/network. Unregistering client queue.")
            notifier_broker.unregister_client(client_queue)
            raise
        except Exception as e:
            logger.error(f"Error inside SSE event generator: {e}")
            notifier_broker.unregister_client(client_queue)
            raise

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/status")
async def system_status():
    return {
        "db_backend_config": settings.DB_BACKEND,
        "db_backend_active": "local_json" if db_manager.use_fallback else "mongodb",
        "groq_api_configured": settings.GROQ_API_KEY is not None and len(settings.GROQ_API_KEY) > 0,
        "time": datetime.now().isoformat()
    }
