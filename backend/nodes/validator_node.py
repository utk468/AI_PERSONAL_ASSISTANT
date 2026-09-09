import logging
from datetime import datetime, timedelta
from backend.nodes.state import IntentState

logger = logging.getLogger("assistant.nodes.validator")

def validator_node(state: IntentState) -> dict:
    """LangGraph Node: Validates extracted intent for logical consistency & time resolution."""
    intent = state.get("intent")
    current_time = state.get("current_time", datetime.now())

    if not intent:
        logger.warning("[LangGraph Node: Validator] No intent object to validate.")
        return {"is_valid": False, "error_msg": "Missing intent object"}

    if not intent.task or not intent.task.strip():
        logger.warning("[LangGraph Node: Validator] Empty task description detected.")
        return {"is_valid": False, "error_msg": "Task description is empty"}

    # Ensure extracted_datetime is populated
    if not intent.extracted_datetime:
        logger.info("[LangGraph Node: Validator] Missing extracted_datetime. Calculating next run...")
        intent.extracted_datetime = _calculate_next_run(intent, current_time)

    # Check if extracted time is valid ISO format
    try:
        dt = datetime.fromisoformat(intent.extracted_datetime)
    except Exception as e:
        logger.warning(f"[LangGraph Node: Validator] Invalid datetime ISO string: {intent.extracted_datetime}")
        return {"is_valid": False, "error_msg": f"Invalid datetime string: {e}"}

    logger.info(f"[LangGraph Node: Validator] Intent validated successfully for task: '{intent.task}' at {intent.extracted_datetime}")
    return {"is_valid": True, "error_msg": None}


def _calculate_next_run(intent, current_time: datetime) -> str:
    target_hour = 9
    target_minute = 0

    if intent.time_of_day:
        try:
            h, m = map(int, intent.time_of_day.split(":"))
            target_hour, target_minute = h, m
        except:
            pass

    if intent.is_recurring:
        if intent.recurrence_pattern == "hourly":
            return (current_time + timedelta(hours=1)).replace(second=0, microsecond=0).isoformat()

        next_run = current_time.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if next_run <= current_time:
            next_run += timedelta(days=1)
        return next_run.isoformat()
    else:
        if intent.date_str:
            try:
                parsed_date = datetime.strptime(intent.date_str, "%Y-%m-%d")
                return parsed_date.replace(hour=target_hour, minute=target_minute).isoformat()
            except:
                pass
        return (current_time + timedelta(days=1)).replace(hour=target_hour, minute=target_minute, second=0, microsecond=0).isoformat()
