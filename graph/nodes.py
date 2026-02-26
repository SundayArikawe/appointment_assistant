from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from graph.state import AppointmentState
from tools.appointment_db import (
    get_active_appointment,
    create_appointment,
    reschedule,
    cancel,
)

# Deterministic model
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# =====================================================
# INTENT DETECTION
# =====================================================
def detect_intent(state: AppointmentState) -> AppointmentState:
    state["path_trace"].append("INTENT")

    # 🔥 Do NOT re-detect intent while collecting missing info
    if state.get("status") == "NEED_INFO" and state.get("intent"):
        return state

    prompt = f"""
Classify the user's message into ONE of the following intents:

BOOK
RESCHEDULE
CANCEL
PREPARATION
DEPARTMENT_INFO
UNKNOWN

Message: {state['user_input']}
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip().upper()

    allowed = [
        "BOOK",
        "RESCHEDULE",
        "CANCEL",
        "PREPARATION",
        "DEPARTMENT_INFO",
    ]

    if intent not in allowed:
        intent = "UNKNOWN"

    state["intent"] = intent
    return state


# =====================================================
# RISK CHECK
# =====================================================
def risk_check(state: AppointmentState) -> AppointmentState:
    state["path_trace"].append("RISK")

    emergency_keywords = [
        "chest pain",
        "unconscious",
        "bleeding",
        "severe pain",
        "emergency",
    ]

    if any(word in state["user_input"].lower() for word in emergency_keywords):
        state["risk_flag"] = True
        state["status"] = "ESCALATE"
        state["draft_response"] = (
            f"{state['user_name']}, your message suggests a potential medical emergency. "
            "I cannot provide medical advice. "
            "Please call 911 immediately or visit the nearest emergency department."
        )
        return state

    return state


# =====================================================
# VALIDATION / SLOT FILLING
# =====================================================
def validate_information(state: AppointmentState) -> AppointmentState:
    state["path_trace"].append("VALIDATION")

    if state["status"] == "ESCALATE":
        return state

    intent = state["intent"]
    user_input = state["user_input"].lower()

    if intent == "UNKNOWN":
        state["status"] = "NEED_INFO"
        state["draft_response"] = (
            f"{state['user_name']}, I can help you book, reschedule, cancel, "
            "or provide preparation instructions. What would you like to do?"
        )
        return state

    # ---------------- RESCHEDULE SLOT FILL ----------------
    if intent == "RESCHEDULE":

        # If collecting missing date, use user input directly
        if state.get("status") == "NEED_INFO":
            state["requested_date"] = state["user_input"].strip()
            state["status"] = "IN_PROGRESS"
            return state

        # If no date provided yet, ask for it
        if not state.get("requested_date"):
            state["status"] = "NEED_INFO"
            state["draft_response"] = (
                f"{state['user_name']}, please provide the new date for rescheduling."
            )
            return state

    # ---------------- BOOK SLOT FILL ----------------
    if intent == "BOOK":

        departments = ["mri", "ct scan", "surgery", "cardiology", "neurology"]

        for dept in departments:
            if dept in user_input:
                state["department"] = dept.upper()

        if not state.get("department"):
            state["status"] = "NEED_INFO"
            state["draft_response"] = (
                f"{state['user_name']}, which department would you like to book? "
                "We offer MRI, CT Scan, Surgery, Cardiology, and Neurology."
            )
            return state

        if not state.get("requested_date"):
            state["status"] = "NEED_INFO"
            state["draft_response"] = (
                f"{state['user_name']}, please provide your preferred appointment date."
            )
            return state

    return state


# =====================================================
# EXECUTION
# =====================================================
def execute_action(state: AppointmentState) -> AppointmentState:
    state["path_trace"].append("EXECUTION")

    if state["status"] in ["ESCALATE", "NEED_INFO"]:
        return state

    user = state["user_name"]
    intent = state["intent"]

    # ---------------- RESCHEDULE ----------------
        # ---------------- RESCHEDULE ----------------
    if intent == "RESCHEDULE":

        appointment = get_active_appointment(user)

        # If appointment exists → update it
        if appointment:
            dept, old_date, new_date = reschedule(user, state["requested_date"])

            state["draft_response"] = (
                f"Thank you {user}. Your {dept} appointment has been successfully "
                f"rescheduled from {old_date} to {new_date}."
            )
            state["status"] = "PENDING_REVIEW"
            return state

        # 🔥 If NO appointment exists → create one automatically
        else:
            department = state.get("department") or "General Consultation"

            booked_date = create_appointment(
                user,
                department,
                state["requested_date"]
            )

            state["draft_response"] = (
                f"{user}, you did not have an existing appointment. "
                f"A new {department} appointment has been created for {booked_date} "
                "and marked as rescheduled successfully."
            )
            state["status"] = "PENDING_REVIEW"
            return state

    # ---------------- BOOK ----------------
    if intent == "BOOK":

        booked_date = create_appointment(
            user,
            state["department"],
            state["requested_date"]
        )

        state["draft_response"] = (
            f"Thank you {user}. Your {state['department']} appointment "
            f"has been successfully booked for {booked_date}."
        )
        state["status"] = "PENDING_REVIEW"
        return state

    # ---------------- CANCEL ----------------
    if intent == "CANCEL":

        result = cancel(user)

        if not result:
            state["draft_response"] = (
                f"{user}, you do not currently have a scheduled appointment."
            )
            state["status"] = "PENDING_REVIEW"
            return state

        dept, date = result

        state["draft_response"] = (
            f"Thank you {user}. Your {dept} appointment on {date} "
            "has been cancelled successfully."
        )
        state["status"] = "PENDING_REVIEW"
        return state

    # ---------------- PREPARATION ----------------
       # ---------------- PREPARATION ----------------
    if intent == "PREPARATION":

        appointment = get_active_appointment(user)

        if appointment:
            dept = appointment[1]
        else:
            dept = "your appointment"

        state["draft_response"] = (
            f"{user}, here are general preparation guidelines for {dept}:\n\n"
            "- Arrive 15 minutes early.\n"
            "- Bring a valid ID and insurance information.\n"
            "- Follow any fasting instructions provided.\n"
            "- Inform staff of any medications or conditions.\n"
            "- Contact the clinic if you need clarification.\n\n"
            "If you would like more specific preparation instructions, "
            "please let me know the department."
        )

        state["status"] = "PENDING_REVIEW"
        return state