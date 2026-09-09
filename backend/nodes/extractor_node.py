import logging
from backend.config import settings
from backend.schemas import ReminderIntent
from backend.nodes.state import IntentState

logger = logging.getLogger("assistant.nodes.extractor")

async def llm_extractor_node(state: IntentState) -> dict:
    """LangGraph Node: Uses Groq LLM to extract structured intent from user text."""
    text = state["text"]
    current_time = state["current_time"]

    if not settings.GROQ_API_KEY:
        logger.info("No Groq API Key found. Skipping LLM node.")
        return {"is_valid": False, "error_msg": "No API key configured"}

    try:
        logger.info(f"[LangGraph Node: LLM Extractor] Processing prompt: '{text}'")
        from langchain_groq import ChatGroq
        from langchain_core.prompts import ChatPromptTemplate

        llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name="openai/gpt-oss-20b",
            temperature=0.0
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an AI Personal Assistant intent extractor. Your job is to extract scheduling details "
                "from the user's text reminder request.\n\n"
                "CRITICAL: Current system time context is: {current_time}.\n"
                "All relative terms like 'tomorrow', 'next week', '7 PM' MUST be resolved relative to this exact datetime.\n\n"
                "Extract structured output following the schema strictly."
            )),
            ("human", "User text: \"{text}\"\n\nExtract intent details:")
        ])

        chain = prompt | llm.with_structured_output(ReminderIntent)
        result = await chain.ainvoke({
            "text": text,
            "current_time": current_time.isoformat()
        })

        logger.info(f"[LangGraph Node: LLM Extractor] Extracted: {result.model_dump()}")
        return {"intent": result, "retries": state.get("retries", 0) + 1}

    except Exception as e:
        logger.error(f"[LangGraph Node: LLM Extractor] Failed: {e}")
        return {"is_valid": False, "error_msg": str(e), "retries": state.get("retries", 0) + 1}
