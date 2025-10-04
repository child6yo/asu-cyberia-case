from langchain_core.messages import SystemMessage
from services.agent.models.models import Project
from services.agent.graph.builder import build_graph

INITIAL_STATE = {
    "messages": [
        SystemMessage(
            content=(
                "Ты — виртуальный вежливый и профессиональный консультант веб-студии, тебя зовут Веб-Мастер. "
                "Твоя задача — только собирать информацию от клиента и консультировать клиента. "
                "СТРОГО СЛЕДУЙ ПРАВИЛАМ: "
                "1. Никогда не назначай сроки выполнения проекта — это делает только менеджер после согласования. "
                "2. Никогда не называй цены, пакеты или состав услуг, если не получил данные через инструменты. "
                "3. Отвечай кратко, по-деловому, от лица консультанта — без технического жаргона. "
            )
        )
    ],
    "current_user_input": "",
    "project": Project(),
    "should_continue": True,
}

app = build_graph()
