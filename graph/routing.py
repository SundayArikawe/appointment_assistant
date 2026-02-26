from langgraph.graph import StateGraph, END
from graph.state import AppointmentState
from graph.nodes import (
    detect_intent,
    risk_check,
    validate_information,
    execute_action,
)
from middleware.moderation import moderation_check
from middleware.hitl import human_review


def build_graph():
    builder = StateGraph(AppointmentState)

    builder.add_node("moderation", moderation_check)
    builder.add_node("intent", detect_intent)
    builder.add_node("risk", risk_check)
    builder.add_node("validation", validate_information)
    builder.add_node("execution", execute_action)
    builder.add_node("hitl", human_review)

    builder.set_entry_point("moderation")

    builder.add_edge("moderation", "intent")
    builder.add_edge("intent", "risk")
    builder.add_edge("risk", "validation")
    builder.add_edge("validation", "execution")
    builder.add_edge("execution", "hitl")
    builder.add_edge("hitl", END)

    return builder.compile()