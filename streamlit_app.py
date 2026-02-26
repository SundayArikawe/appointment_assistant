import streamlit as st
from dotenv import load_dotenv
from graph.state import initialize_state
from graph.routing import build_graph
from middleware.pii import apply_pii_masking
from tools.appointment_db import init_db

load_dotenv()
init_db()
app = build_graph()

st.title("🏥 AI Healthcare Appointment Assistant")

if "state" not in st.session_state:
    st.session_state.state = None

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if not st.session_state.user_name:
    name = st.text_input("Enter your name")
    if name:
        st.session_state.user_name = name
        st.success(f"Welcome {name}!")
        st.rerun()

user_input = st.text_input("Ask your question:")

if st.button("Submit") and user_input:

    if st.session_state.state is None:
        state = initialize_state(user_input, st.session_state.user_name)
        state["hitl_mode"] = "AUTO_APPROVE"
    else:
        state = st.session_state.state
        state["user_input"] = user_input
        # Keep NEED_INFO flow active so follow-up answers are handled correctly.
        if state.get("status") != "NEED_INFO":
            state["status"] = "IN_PROGRESS"

    final_state = app.invoke(state)
    final_state = apply_pii_masking(final_state)

    st.session_state.state = final_state

    st.markdown("### Assistant Response:")
    st.write(final_state.get("final_response"))
