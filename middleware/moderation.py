def moderation_check(state):
    state["path_trace"].append("MODERATION")

    unsafe_keywords = ["harm someone", "kill", "attack"]

    if any(word in state["user_input"].lower() for word in unsafe_keywords):
        state["status"] = "ESCALATE"
        state["draft_response"] = (
            "Your message contains unsafe content. "
            "This assistant cannot support harmful requests."
        )
        return state

    return state