from langchain_core.messages import HumanMessage, AIMessage
from services.agent.models.models import SystemState
from services.agent.llm.client import simple_llm
from services.agent.utils.messages import get_last_human_message


def entry_node(state: SystemState) -> dict:
    user_input = get_last_human_message(state)
    try:
        messages = state["messages"] + [
            HumanMessage(
                content="""Необходимо поприветствовать пользователя. 
                Далее спросить, название будущего проекта пользователя и его контактные данные, включающие имя, email и телефонный номер."""
            )
        ]
        response = simple_llm.invoke(messages)
        ai_response = response.content
        new_messages = messages + [AIMessage(content=ai_response)]
        return {"messages": new_messages}
    except Exception as e:
        messages = state["messages"] + [
            HumanMessage(content=user_input),
            AIMessage(
                content="Извините, произошла ошибка при обработке вашего вопроса."
            ),
        ]
        return {"messages": messages}
