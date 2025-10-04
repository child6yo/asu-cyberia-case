from langchain_core.messages import SystemMessage
from services.agent.models.models import Project
from graph.builder import build_graph

INITIAL_STATE = {
    "messages": [
        SystemMessage(
            content="Ты продавец-консультант веб-студии. Поприветствуй пользователя..."
        )
    ],
    "current_user_input": "",
    "project": Project(),
    "should_continue": True,
}

app = build_graph()
