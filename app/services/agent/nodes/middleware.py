from services.agent.models.models import *
from services.agent.llm.client import *
from langchain_core.messages import HumanMessage, AIMessage


def middleware_node(state: SystemState) -> dict:
    try:
        messages = state["messages"] + [
            HumanMessage(
                content=f"""Если пользователь попал сюда - значит его сообщение выпадает из общего контекста.
                Если сообщение просто бессмысленно в рамках контекста - уточни его.
                Если сообщение - вопрос, - попробуй на него ответить, при этом, если ответ на вопрос ты не знаешь 
                (он ранее не упоминался и не понятен) - так и ответь - НЕ ЗНАЮ."""
            )
        ]
        response = simple_llm.invoke(messages)
        new_messages = messages + [AIMessage(content=response.content)]
        return {"messages": new_messages}
    except Exception as e:
        return {
            "messages": state["messages"] + [AIMessage(content="Извините, ошибка...")]
        }
