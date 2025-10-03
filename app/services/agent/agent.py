from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv
import os

from services.agent.models import *
from services.agent.tools.tools import tools_list

load_dotenv()

CRED = os.getenv("GIGACHAT_CRED")

simple_llm = GigaChat(
    credentials=CRED,
    scope="GIGACHAT_API_PERS",
    model="GigaChat-2",
    verify_ssl_certs=False,
    temperature=0.4,
)

llm = GigaChat(
    credentials=CRED,
    scope="GIGACHAT_API_PERS",
    model="GigaChat-2",
    verify_ssl_certs=False,
    temperature=0.2,
).bind_tools(tools_list)


def get_last_human_message(state: SystemState) -> str:
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


def entry_node(state: SystemState) -> dict:
    user_input = get_last_human_message(state)

    try:
        messages = state["messages"] + [
            HumanMessage(
                content=f"""Необходимо поприветствовать пользователя. 
                Далее спросить, название будущего проекта пользователя и его контактные данные, включающие имя, email и телефонный номер."""
            )
        ]

        response = simple_llm.invoke(messages)
        ai_response = response.content

        print(ai_response)

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


def parse_customer_node(state: SystemState) -> dict:
    customer_parser = JsonOutputParser(pydantic_object=Customer)
    customer_prompt = PromptTemplate(
        template="""Вычлени из сообщения необходимую информацию о пользователе. 
    Если чего-то не хватает - заполни только те поля, информацию о которых пользователь предоставил.

    Сообщение: {user_input}

    {format_instructions}

    Верни ТОЛЬКО JSON!""",
        input_variables=["user_input"],
        partial_variables={
            "format_instructions": customer_parser.get_format_instructions()
        },
    )
    user_input = get_last_human_message(state)
    messages = state["messages"]
    new_messages = messages + [HumanMessage(content=user_input)]

    try:
        parser_chain = customer_prompt | llm | customer_parser
        result = parser_chain.invoke({"user_input": user_input})

        return {
            "messages": new_messages,
            "project": {
                "customer": {
                    "name": result.get("name"),
                    "email": result.get("email"),
                    "phone": result.get("phone"),
                }
            },
        }

    except Exception as e:
        print(f"Ошибка парсинга клиента: {e}")
        return {
            "messages": new_messages,
            "project": {
                "customer": {
                    "name": None,
                    "email": None,
                    "phone": None,
                }
            },
        }


def parse_project_name_node(state: SystemState) -> dict:
    project_name_prompt = PromptTemplate(
        template="""Извлеки из сообщения пользователя ТОЛЬКО название его будущего проекта. 
    Если название упомянуто — верни его дословно, без кавычек, без пояснений, без дополнительного текста.
    Если название не упомянуто — верни "Без названия".

    Сообщение: {user_input}

    Верни ТОЛЬКО НАЗВАНИЕ.
    """,
        input_variables=["user_input"],
    )

    user_input = get_last_human_message(state)

    try:
        chain = project_name_prompt | simple_llm
        result = chain.invoke({"user_input": user_input})
        project_name = result.content.strip()
    except Exception as e:
        print(f"Ошибка: {e}")
        project_name = "Без названия"

    current_project = state.get("project", {})
    updated_project = {
        "name": project_name,
        "customer": current_project.get("customer", {}),
    }
    return {"project": updated_project}


def project_type_node(state: SystemState) -> dict:
    print(state["project"])

    try:
        messages = state["messages"] + [
            HumanMessage(
                content=f"Теперь необходимо спросить о типе проекта, описании и основных пожеланиях по функционалу. Возможные типы проектов, которые возможно выполнить: {project_types}."
            )
        ]

        response = simple_llm.invoke(messages)
        ai_response = response.content

        print(ai_response)

        new_messages = messages + [AIMessage(content=ai_response)]
        return {"messages": new_messages}

    except Exception as e:
        messages = state["messages"] + [
            AIMessage(
                content="Извините, произошла ошибка при обработке вашего вопроса."
            ),
        ]

        return {"messages": messages}


def parse_project_type_node(state: SystemState) -> dict:
    requirements_parser = JsonOutputParser(pydantic_object=Requirements)
    requirements_prompt = PromptTemplate(
        template="""Вычлени из сообщения всю информацию о проекте, включающую:
    - тип проекта (Создание корпоративного сайта, Создание интернет-магазина, Создание простого лендинга)
    - дополнительные опции (пожелания по проекту)

    Сообщение: {user_input}

    {format_instructions}

    НЕ ДОБАВЛЯЙ НИКАКИХ КОММЕНТАРИЕВ. ВЕРНИ ТОЛЬКО JSON.""",
        input_variables=["user_input"],
        partial_variables={
            "format_instructions": requirements_parser.get_format_instructions()
        },
    )

    user_input = get_last_human_message(state)
    messages = state["messages"]
    new_messages = messages + [HumanMessage(content=user_input)]

    try:
        chain = requirements_prompt | llm | requirements_parser
        result = chain.invoke({"user_input": user_input})
        requirements_type = result.get("type")
        requirements_options = result.get("options")
    except Exception as e:
        print(f"Ошибка: {e}")

    current_project = state.get("project", {})
    updated_project = {
        "name": current_project.get("name", "Без названия"),
        "customer": current_project.get("customer", {}),
        "requirements": {
            "type": requirements_type,
            "options": requirements_options,
        },
    }
    return {
        "messages": new_messages,
        "project": updated_project,
    }


def parse_project_description_node(state: SystemState) -> dict:
    project_description_prompt = PromptTemplate(
        template="""Извлеки из сообщения пользователя ТОЛЬКО краткое описание проекта. 
    Если это невозможно — верни "Без описания".

    Сообщение: {user_input}

    Верни ТОЛЬКО ОПИСАНИЕ.
    """,
        input_variables=["user_input"],
    )

    user_input = get_last_human_message(state)

    try:
        chain = project_description_prompt | llm
        result = chain.invoke({"user_input": user_input})
        project_description = result.content.strip()
    except Exception as e:
        print(f"Ошибка: {e}")

    current_project = state.get("project", {})
    updated_project = {
        "name": current_project.get("name", "Без названия"),
        "customer": current_project.get("customer", {}),
        "description": project_description,
        "requirements": current_project.get("requirements", {}),
    }
    print(updated_project)
    return {"project": updated_project}


def detalize_node(state: SystemState) -> dict:
    messages = list(state["messages"]) + [
        HumanMessage(
            f"""
            Проанализируй прайс-лист по {state['project']['requirements']['type']},
            сопоставь с требованиями пользователя (ТРЕБОВАНИЯ: {state['project']['requirements']['options']}).
            Озвучь требуемые услуги и предложи дополнительные опции, которые подошли бы
            по описанию {state['project']['description']}.

            Спроси пользователя, верно ли все озвучено. Если что-то не верно — пользователь должен объяснить.
            """
        )
    ]
    response = llm.invoke(messages)
    print(response.content)

    return {"messages": [response]}


def check_details_node(state: SystemState) -> dict:
    agreement_parser = JsonOutputParser(pydantic_object=UserAgreement)
    agreement_prompt = PromptTemplate(
        template="""Ты — строгий парсер. Твоя задача — проанализировать сообщение пользователя и выдать ТОЛЬКО валидный JSON в формате:
    {format_instructions}

    Сообщение пользователя: {user_input}

    НЕ ДОБАВЛЯЙ НИКАКИХ КОММЕНТАРИЕВ. ВЕРНИ ТОЛЬКО JSON.""",
        input_variables=["user_input"],
        partial_variables={
            "format_instructions": agreement_parser.get_format_instructions()
        },
    )

    user_input = get_last_human_message(state)
    messages = state["messages"]
    new_messages = messages + [HumanMessage(content=user_input)]

    try:
        chain = agreement_prompt | llm | agreement_parser
        result = chain.invoke({"user_input": user_input})

        if isinstance(result, str):
            result_lower = result.strip().lower()
            if (
                "true" in result_lower
                or "соглас" in result_lower
                or "да" in result_lower
            ):
                agreement = True
            else:
                agreement = False
        else:
            agreement = result.get("is_user_agree", False)

    except Exception as e:
        print(f"Ошибка парсинга согласия: {e}")
        agreement = False

    return {"messages": new_messages, "should_continue": agreement}


def correcting_node(state: SystemState) -> dict:
    user_input = get_last_human_message(state)

    correction_parser = JsonOutputParser(pydantic_object=Requirements)
    correction_prompt = PromptTemplate(
        template="""Пользователь указал, что в предыдущем описании есть ошибки.
        На основе его комментария извлеки обновлённые требования к проекту.

        Текущие требования: {requirements}
        Текущее описание: {description}
        Комментарий пользователя: {user_input}

        {format_instructions}

        НЕ ДОБАВЛЯЙ НИКАКИХ КОММЕНТАРИЕВ. ВЕРНИ ТОЛЬКО JSON.""",
        input_variables=["user_input"],
        partial_variables={
            "format_instructions": correction_parser.get_format_instructions()
        },
    )

    try:
        chain = correction_prompt | llm | correction_parser
        updated_requirements = chain.invoke(
            {
                "user_input": user_input,
                "requirements": state["project"]["requirements"],
                "description": state["project"]["description"],
            }
        )

        current_req = state["project"]["requirements"]
        new_req = {}

        if updated_requirements.get("type") is not None:
            new_req["type"] = updated_requirements["type"]
        else:
            new_req["type"] = current_req.get("type")

        if updated_requirements.get("options") is not None:
            new_req["options"] = updated_requirements["options"]
        else:
            new_req["options"] = current_req.get("options", [])

        updated_project = {**state["project"], "requirements": new_req}

        return {
            "project": updated_project,
            "should_continue": True,
        }

    except Exception as e:
        print(f"Ошибка при обработке корректировок: {e}")
        return {"should_continue": True}


def budget_node(state: SystemState) -> dict:
    try:
        messages = state["messages"] + [
            HumanMessage(
                content="Теперь необходимо спросить о бюджете пользователя и о сроках, за которые необходимо выполнить проект."
            )
        ]

        response = simple_llm.invoke(messages)
        ai_response = response.content

        print(ai_response)

        new_messages = messages + [AIMessage(content=ai_response)]
        return {"messages": new_messages}

    except Exception as e:
        messages = state["messages"] + [
            AIMessage(
                content="Извините, произошла ошибка при обработке вашего вопроса."
            ),
        ]

        return {"messages": messages}


def parse_budget_node(state: SystemState) -> dict:
    budget_parser = JsonOutputParser(pydantic_object=Estimate)
    budget_prompt = PromptTemplate(
        template="""Ты — строгий парсер. Твоя задача — проанализировать сообщение пользователя и выдать ТОЛЬКО валидный JSON в формате:
    {format_instructions}

    Сообщение пользователя: {user_input}

    НЕ ДОБАВЛЯЙ НИКАКИХ КОММЕНТАРИЕВ. ВЕРНИ ТОЛЬКО JSON.""",
        input_variables=["user_input"],
        partial_variables={
            "format_instructions": budget_parser.get_format_instructions()
        },
    )

    user_input = get_last_human_message(state)
    messages = state["messages"]
    new_messages = messages + [HumanMessage(content=user_input)]

    try:
        chain = budget_prompt | llm | budget_parser
        result = chain.invoke({"user_input": user_input})

        updated_project = {
            **state["project"],
            "estimate": {
                "budget": result.get("budget"),
                "time": result.get("time"),
            },
        }

        return {"messages": new_messages, "project": updated_project}

    except Exception as e:
        print(f"Ошибка парсинга бюджета: {e}")

        return {"messages": new_messages}


def budget_analysis_node(state: SystemState) -> dict:
    messages = list(state["messages"]) + [
        HumanMessage(
            f"""
            Проанализируй прайс-лист по {state['project']['requirements']['type']},
            учти доп. опции, которые выбрал пользователь - {state['project']['requirements']['options']},
            сопоставь с бюджетом пользователя - {state['project']['estimate']['budget']} и
            с требованиями пользователя по времени - {state['project']['estimate']['time']}

            Если что-то не вписывается в рамки - предложи альтернативы, либо предложи пользователю увеличить сроки/бюджет.
            Иными словами, если запросы пользователя не вписываются в прайс-лист - предложи компромисс.
            """
        )
    ]
    response = llm.invoke(messages)
    print(response.content)

    return {"messages": [response]}


def parse_budget_analysis_node(state: SystemState) -> dict:
    budget_analysis_parser = JsonOutputParser(pydantic_object=UserBudgetSufficiency)
    budget_analysis_prompt = PromptTemplate(
        template="""Ты — строгий парсер. Твоя задача — проанализировать сообщение консультанта и сказать, 
        устроил ли его бюджет пользователя и его требования по срокам. 
        Завернуть это НЕОБХОДИМО в валидный JSON формата:
    {format_instructions}

    Сообщение консультанта: {ai_input}

    НЕ ДОБАВЛЯЙ НИКАКИХ КОММЕНТАРИЕВ. ВЕРНИ ТОЛЬКО JSON.""",
        input_variables=["ai_input"],
        partial_variables={
            "format_instructions": budget_analysis_parser.get_format_instructions()
        },
    )

    try:
        chain = budget_analysis_prompt | llm | budget_analysis_parser
        result = chain.invoke({"ai_input": state["messages"][-1].content})

        if isinstance(result, str):
            result_lower = result.strip().lower()
            if "true" in result_lower or "да" in result_lower:
                sufficiency = True
            else:
                sufficiency = False
        else:
            sufficiency = result.get("state", False)

    except Exception as e:
        print(f"Ошибка парсинга анализа бюджета: {e}")
        sufficiency = False

    return {"should_continue": sufficiency}


def budget_correcting_node(state: SystemState) -> dict:
    user_input = get_last_human_message(state)
    messages = state["messages"]
    new_messages = messages + [HumanMessage(content=user_input)]

    try:
        response = simple_llm.invoke(new_messages)
        ai_response = response.content

        print(ai_response)

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


def final_node(state: SystemState) -> dict:
    print(state["project"])
    return {
        "messages": state["messages"]
        + [AIMessage(content="Спасибо! Ваш проект сохранён.")]
    }


graph = StateGraph(SystemState)

graph.add_node("entry", entry_node)
graph.add_node("parse_customer", parse_customer_node)
graph.add_node("parse_project_name", parse_project_name_node)
graph.add_node("project_type", project_type_node)
graph.add_node("parse_project_type", parse_project_type_node)
graph.add_node("parse_project_description", parse_project_description_node)
graph.add_node("detalize", detalize_node)
graph.add_node("check_details", check_details_node)
graph.add_node("correcting", correcting_node)
graph.add_node("final", final_node)
tool_node = ToolNode(tools=tools_list)
graph.add_node("tools_after_detalize", tool_node)
graph.add_node("budget", budget_node)
graph.add_node("tools_after_budget", tool_node)
graph.add_node("parse_budget", parse_budget_node)
graph.add_node("budget_analysis", budget_analysis_node)
graph.add_node("budget_correcting", budget_correcting_node)


def route_after_input(state: SystemState) -> str:
    return "continue" if state.get("should_continue", True) else "back"


def route_before_tools(state: SystemState) -> str:
    messages = state["messages"]
    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "continue"

    return "end"


graph.add_edge(START, "entry")
graph.add_edge("entry", "parse_customer")
graph.add_edge("parse_customer", "parse_project_name")
graph.add_edge("parse_project_name", "project_type")
graph.add_edge("project_type", "parse_project_type")
graph.add_edge("parse_project_type", "parse_project_description")
graph.add_edge("parse_project_description", "detalize")
graph.add_conditional_edges(
    "detalize",
    route_before_tools,
    {"continue": "tools_after_detalize", "end": "check_details"},
)
graph.add_edge("tools_after_detalize", "detalize")
graph.add_conditional_edges(
    "check_details",
    route_after_input,
    {
        "continue": "budget",
        "back": "correcting",
    },
)
graph.add_edge("correcting", "detalize")
graph.add_edge("budget", "parse_budget")
graph.add_edge("parse_budget", "budget_analysis")
graph.add_conditional_edges(
    "budget_analysis",
    route_before_tools,
    {"continue": "tools_after_budget", "end": "parse_budget_analysis"},
)
graph.add_edge("tools_after_budget", "budget_analysis")
graph.add_conditional_edges(
    "parse_budget_analysis",
    route_after_input,
    {
        "continue": "final",
        "back": "budget_correcting",
    },
)
graph.add_edge("budget_correcting", "parse_budget")
graph.add_edge("final", END)

memory = MemorySaver()
app = graph.compile(
    checkpointer=memory,
    interrupt_after=[
        "entry",
        "project_type",
        "detalize",
        "budget",
        "parse_budget_analysis",
    ],
)
INITIAL_STATE = {
    "messages": [
        SystemMessage(
            content="Ты продавец-консультант веб-студии. Кратко поприветствуй пользователя. Вежливо собирай информацию с пользователя о проекте, который ему нужен."
        )
    ],
    "current_user_input": "",
    "project": Project(),
    "should_continue": True,
}
