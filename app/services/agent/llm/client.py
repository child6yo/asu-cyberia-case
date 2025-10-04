from langchain_openai import ChatOpenAI
from services.agent.tools import tools_list
from services.agent.config.settings import LLM_CRED

simple_llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=LLM_CRED,
    model="deepseek/deepseek-chat-v3.1:free",
    temperature=0.1,
    max_tokens=2048,
)

llm_with_tools = simple_llm.bind_tools(tools_list)
