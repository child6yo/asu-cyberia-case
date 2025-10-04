from langchain_gigachat.chat_models import GigaChat
from services.agent.config.settings import GIGACHAT_CRED
from services.agent.tools import tools_list

simple_llm = GigaChat(
    credentials=GIGACHAT_CRED,
    scope="GIGACHAT_API_PERS",
    model="GigaChat-2",
    verify_ssl_certs=False,
    temperature=0.4,
)

llm_with_tools = GigaChat(
    credentials=GIGACHAT_CRED,
    scope="GIGACHAT_API_PERS",
    model="GigaChat-2-Max",
    verify_ssl_certs=False,
    temperature=0.2,
).bind_tools(tools_list)