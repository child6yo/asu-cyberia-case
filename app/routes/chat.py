from fastapi import APIRouter
from schemas.chat import *
from services.agent.agent import INITIAL_STATE, app
from langchain_core.messages import AIMessage, HumanMessage

router = APIRouter(prefix="/api", tags=["query"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_id = request.user_id
    user_message = request.message
    config = {"configurable": {"thread_id": user_id}}

    current_checkpoint = app.get_state(config)

    if current_checkpoint.next:
        pass
    else:
        app.update_state(config, INITIAL_STATE)

    app.update_state(config, {"messages": [HumanMessage(content=user_message)]})

    for _ in app.stream(None, config):
        pass

    final_state = app.get_state(config).values
    last_message = final_state["messages"][-1]

    response_text = last_message.content if isinstance(last_message, AIMessage) else "…"

    return ChatResponse(
        response=response_text,
        project=final_state["project"],
        finished=False,
    )
