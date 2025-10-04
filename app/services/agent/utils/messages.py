from langchain_core.messages import HumanMessage
from app.services.agent.models.models import SystemState

def get_last_human_message(state: SystemState) -> str:
    for msg in reversed(state.messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""