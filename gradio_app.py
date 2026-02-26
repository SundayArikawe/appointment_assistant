from dotenv import load_dotenv
import gradio as gr

from graph.routing import build_graph
from graph.state import initialize_state
from middleware.pii import apply_pii_masking
from tools.appointment_db import init_db


load_dotenv()
init_db()
app = build_graph()


def _reset_session():
    return [], {"user_name": "", "state": None}


def _handle_message(message, history, session):
    history = history or []
    session = session or {"user_name": "", "state": None}

    user_input = (message or "").strip()
    if not user_input:
        return "", history, session

    if not session.get("user_name"):
        session["user_name"] = user_input
        history.append((None, f"Welcome {session['user_name']}! Ask your question."))
        return "", history, session

    state = session.get("state")
    if state is None:
        state = initialize_state(user_input, session["user_name"])
        state["hitl_mode"] = "AUTO_APPROVE"
    else:
        state["user_input"] = user_input
        if state.get("status") != "NEED_INFO":
            state["status"] = "IN_PROGRESS"

    final_state = app.invoke(state)
    final_state = apply_pii_masking(final_state)

    assistant_text = final_state.get("final_response") or final_state.get("draft_response")
    history.append((user_input, assistant_text))

    if final_state.get("status") in ["READY", "ESCALATE"]:
        session["state"] = None
    else:
        session["state"] = final_state

    return "", history, session


with gr.Blocks(title="AI Healthcare Appointment Assistant") as demo:
    gr.Markdown("## AI Healthcare Appointment Assistant")
    gr.Markdown("Enter your name first, then continue with your appointment requests.")
    chatbot = gr.Chatbot(label="Assistant")
    session_state = gr.State({"user_name": "", "state": None})
    msg = gr.Textbox(label="Your message", placeholder="Type here and press Enter")
    clear = gr.Button("Reset Session")

    msg.submit(_handle_message, [msg, chatbot, session_state], [msg, chatbot, session_state])
    clear.click(_reset_session, outputs=[chatbot, session_state])


if __name__ == "__main__":
    demo.launch()
