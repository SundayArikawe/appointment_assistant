from graph.state import initialize_state
from graph.routing import build_graph

app = build_graph()

state = initialize_state("I want to reschedule my appointment.", "TestUser")

final_state = app.invoke(state)

print("\nFINAL GRAPH STATE:\n")
print(final_state)
