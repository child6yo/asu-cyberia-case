from langchain_core.messages import AIMessage
from services.agent.models.models import SystemState


def route_after_input(state: SystemState) -> str:
    return "continue" if state.should_continue else "back"


def route_before_tools(state: SystemState) -> str:
    last_message = state.messages[-1]
    if isinstance(last_message, AIMessage) and getattr(
        last_message, "tool_calls", None
    ):
        return "continue"
    return "end"
