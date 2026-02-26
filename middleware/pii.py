import re


def apply_pii_masking(state):
    if state.get("final_response"):
        state["final_response"] = re.sub(
            r"APT-\w+", "APT-***", state["final_response"]
        )
    return state