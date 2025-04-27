from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# --- Define State Schema ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    automation_output: str