import logging
from datetime import datetime
from langgraph.graph import StateGraph, END

from backend.schemas import ReminderIntent
from backend.nodes.state import IntentState
from backend.nodes.extractor_node import llm_extractor_node
from backend.nodes.validator_node import validator_node, _calculate_next_run

logger = logging.getLogger("assistant.graph")


def route_validation(state: IntentState) -> str:
    """Conditional Edge Router: End if valid or if max retries reached; retry LLM if invalid."""
    if state.get("is_valid"):
        logger.info("[LangGraph Router] State valid. Routing to END.")
        return "end"
    
    retries = state.get("retries", 0)
    if retries >= 2:
        logger.warning("[LangGraph Router] Max retries reached for LLM node. Finishing graph.")
        return "end"
        
    logger.warning(f"[LangGraph Router] LLM validation failed ('{state.get('error_msg')}'). Retrying LLM extractor...")
    return "retry"


def build_intent_graph():
    """Builds and compiles the pure LLM-driven LangGraph StateGraph pipeline."""
    workflow = StateGraph(IntentState)

    # Add LLM & Validator Nodes
    workflow.add_node("llm_extractor", llm_extractor_node)
    workflow.add_node("validator", validator_node)

    # Set entry point
    workflow.set_entry_point("llm_extractor")

    # Connect edges
    workflow.add_edge("llm_extractor", "validator")

    # Add conditional branching edge from validator
    workflow.add_conditional_edges(
        "validator",
        route_validation,
        {
            "end": END,
            "retry": "llm_extractor"
        }
    )

    return workflow.compile()


# Compile global graph instance
compiled_intent_graph = build_intent_graph()


class IntentGraphExtractor:
    """Interface wrapper for pure LLM-driven intent extraction via LangGraph."""

    async def extract(self, text: str, current_time: datetime) -> ReminderIntent:
        initial_state: IntentState = {
            "text": text,
            "current_time": current_time,
            "intent": None,
            "is_valid": False,
            "error_msg": None,
            "retries": 0
        }

        logger.info(f"[LangGraph Execution] Running pure LLM intent extraction graph for: '{text}'")
        final_state = await compiled_intent_graph.ainvoke(initial_state)

        intent = final_state.get("intent")
        if not intent:
            raise RuntimeError(f"LLM Intent extraction failed: {final_state.get('error_msg') or 'No response from LLM'}")

        return intent

    def _calculate_next_run(self, intent: ReminderIntent, current_time: datetime) -> str:
        return _calculate_next_run(intent, current_time)


intent_extractor = IntentGraphExtractor()
