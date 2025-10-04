from services.agent.models.models import SystemState
from langchain_core.messages import AIMessage
from repository.memory.projects import projects_volume


def final_node(state: SystemState) -> dict:
    print(state["project"])
    projects_volume.Put(state["project"])
    return {
        "messages": state["messages"]
        + [AIMessage(content="Спасибо! Ваш проект сохранён.")]
    }
