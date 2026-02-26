from graph.state import initialize_state
from graph.nodes import detect_intent, risk_check

# Try different scenarios
state = initialize_state(
    "I want to reschedule my appointment to next Monday.", "TestUser"
)

state = detect_intent(state)
state = risk_check(state)

print("\nFINAL STATE:\n")
print(state)
