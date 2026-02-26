MBAN 5510 – Final Project

Appointment Assistance System (LangGraph Middleware Orchestration)
Autho:
Arikawe Sunday

Project Overview

This project implements a middleware-driven appointment assistance system using LangGraph.

The system is designed to demonstrate:

Stateful workflow orchestration

Conditional routing

Middleware layering

Human-in-the-Loop (HITL) governance

Risk-based escalation

Privacy (PII masking) controls

Clear terminal state enforcement

This is not a simple chatbot. It is a structured orchestration engine that uses a shared state object flowing through multiple middleware layers.

2 Core Objectives

The system must:

Handle appointment rescheduling

Handle cancellation

Provide preparation instructions

Detect emergency medical language

Detect harmful content

Avoid giving medical advice

Require human approval before final output

Mask sensitive identifiers before logging

3 High-Level Architecture

The system is built using a LangGraph StateGraph.

Workflow Overview
User Input
   ↓
MODERATION_CHECK
   ↓
INTENT_DETECTION
   ↓
RISK_CHECK
   ↓
VALIDATION
   ↓
EXECUTION
   ↓
HITL_REVIEW
   ↓
PII_MASKING
   ↓
END

Each node reads and mutates a shared state object (AppointmentState).

Routing decisions are handled through conditional edges.

4 File Structure Explained
appointment_assistant/
│
├── graph/
│   ├── state.py
│   ├── nodes.py
│   └── routing.py
│
├── middleware/
│   ├── moderation.py
│   ├── hitl.py
│   └── pii.py
│
├── tools/
│   └── appointment_db.py
│
├── main.py
└── .env
5 The Shared State (graph/state.py)

This file defines:

class AppointmentState(TypedDict)

This is the central data structure that flows through the graph.

It contains:

run_id → unique execution identifier

timestamp → audit trail

user_name → personalized session tracking

user_input → current message

intent → classified action

appointment_id → mock ID

requested_date → extracted date

risk_flag → emergency detection

missing_info → validation tracking

status → IN_PROGRESS / READY / NEED_INFO / ESCALATE

path_trace → logs every node visited

draft_response → pre-review message

final_response → approved output

human_action → reviewer decision

Every node reads and modifies this same state object.

This ensures traceability and governance transparency.

6️ Middleware Layers

The system includes multiple middleware components:

🔹 6.1 Moderation Middleware (middleware/moderation.py)

Purpose:

Detect harmful or violent language

Block unsafe requests before intent detection

If triggered:

Sets risk_flag = True

Sets status = ESCALATE

Short-circuits workflow

This demonstrates responsible AI content filtering.

🔹 6.2 Risk Check (Medical Emergency Detection)

Inside nodes.py:

def risk_check(state):

This checks for emergency keywords like:

chest pain

bleeding

severe pain

unconscious

If detected:

status → ESCALATE

workflow stops

supportive message is generated

⚠ Important Governance Rule:

The system does not provide medical advice.

It explicitly states:

I am not able to provide medical advice…

It directs users to emergency services instead.

This complies with the project requirement:

The system must not provide clinical advice.

🔹 6.3 Validation Layer

If intent is UNKNOWN:

status → NEED_INFO

user asked to clarify

If rescheduling without a date:

status → NEED_INFO

asks for date

This prevents execution with incomplete information.

🔹 6.4 Human-in-the-Loop (middleware/hitl.py)

After execution:

A draft response is generated

CLI pauses

Reviewer chooses:

Approve

Edit

Escalate

The system never finalizes output without human approval.

This enforces governance and accountability.

🔹 6.5 PII Masking Middleware (middleware/pii.py)

Before printing final output:

Appointment IDs like:

APT-123

are masked to:

APT-***

This prevents sensitive information exposure in logs.

This fulfills privacy best practices.

7️ Step-by-Step Execution Flow

Let’s walk through an example.

Scenario 1 — Normal Reschedule

User:

I want to reschedule my appointment to Tuesday

Step-by-step:

Moderation → No issues

Intent Detection → RESCHEDULE

Risk Check → No emergency

Validation → Extracts “Tuesday”

Execution → Calls reschedule tool

HITL → Requires approval

PII Masking → Masks ID

Final output shown

Terminal Status: READY

Scenario 2 — Ambiguous Input

User:

I need help

Flow:

Moderation → OK

Intent Detection → UNKNOWN

Validation → NEED_INFO

No execution

System asks clarification

Terminal Status: NEED_INFO

Scenario 3 — Emergency

User:

I have severe chest pain

Flow:

Moderation → OK

Intent Detection → Possibly UNKNOWN

Risk Check → Emergency triggered

status → ESCALATE

Execution skipped

HITL finalizes

System responds supportively without giving medical advice.

Terminal Status: ESCALATE

8️ Governance Principles Applied

This system demonstrates:

Early content filtering

Risk-based routing

Explicit terminal states

No unsafe continuation

Human oversight

Privacy masking

No clinical advice

The design prioritizes safety over convenience.

9️ Why No Medical Advice Is Given

The project constraint explicitly requires:

The system must not provide clinical advice.

Therefore:

No diagnosis

No treatment suggestions

No medication recommendations

No triage instructions

Only safe redirection to emergency services.

This is intentional and correct.

10 How to Run the System
Step 1 — Install Dependencies
uv add langgraph langchain-openai openai python-dotenv pydantic rich
Step 2 — Create .env
OPENAI_API_KEY=your_api_key_here

Ensure .env is in .gitignore.

Step 3 — Run the System
uv run python main.

11 Session Behavior

The system:

Prompts for user name

Supports multi-turn interactions

Maintains state across turns

Terminates when READY or ESCALATE

12 Why This Is a Middleware-Driven System

Because:

Each layer is independent

Routing is conditional

State is shared

Execution is controlled

Safety can interrupt workflow

The system is not linear — it is orchestrated.

13️ Professional Design Decisions

TypedDict for structured state

Conditional graph routing

Separation of concerns

Explicit status enforcement

CLI session wrapper

Environment variable secrets

PII masking

Human approval checkpoint

14️ Conclusion

This project demonstrates how to build a controlled AI workflow using:

LangGraph orchestration

Middleware governance

Safety constraints

Human oversight

Structured state design

The system prioritizes:

Transparency

Safety

Privacy

Accountability

over raw conversational flexibility.