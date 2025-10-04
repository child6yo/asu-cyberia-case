from langchain_openai import ChatOpenAI
from services.agent.tools import tools_list

simple_llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
    model="deepseek/deepseek-chat-v3.1:free",
    temperature=0.1,
    max_tokens=2048,
)

llm_with_tools = simple_llm.bind_tools(tools_list)
