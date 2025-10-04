from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage
from services.agent.models.models import *
from services.agent.llm.client import *
from services.agent.utils.messages import get_last_human_message


def parse_customer_node(state: SystemState) -> dict:
    customer_parser = JsonOutputParser(pydantic_object=Customer)
    customer_prompt = PromptTemplate(
        template="""Извлеки из сообщения необходимую информацию о пользователе. 
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
        parser_chain = customer_prompt | simple_llm | customer_parser
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


def parse_project_type_node(state: SystemState) -> dict:
    requirements_prompt = PromptTemplate(
        template="""Извлеки из сообщения всю информацию о проекте, включающую:
    - тип проекта (Создание корпоративного сайта, Создание интернет-магазина, Создание простого лендинга)
    - дополнительные опции (пожелания по проекту).

    Сообщение: {user_input}

    Формат, в котором необходимо вернуть информацию:
    'Тип проекта, доп. опция 1, доп. опция 2...'

    НЕ ДОБАВЛЯЙ НИКАКИХ КОММЕНТАРИЕВ. ВЕРНИ ТОЛЬКО ИНФОРМАЦИЮ В НУЖНОМ ФОРМАТЕ.""",
        input_variables=["user_input"],
    )

    user_input = get_last_human_message(state)
    messages = state["messages"]
    new_messages = messages + [HumanMessage(content=user_input)]

    try:
        chain = requirements_prompt | simple_llm
        result = chain.invoke({"user_input": user_input})
        reqs = result.content.strip()
    except Exception as e:
        print(f"Ошибка: {e}")
        reqs = "Не определено"

    current_project = state.get("project", {})
    updated_project = {
        "name": current_project.get("name", "Без названия"),
        "customer": current_project.get("customer", {}),
        "requirements": reqs,
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
        chain = project_description_prompt | simple_llm
        result = chain.invoke({"user_input": user_input})
        project_description = result.content.strip()
    except Exception as e:
        print(f"Ошибка: {e}")
        project_description = "Не определено"

    current_project = state.get("project", {})
    updated_project = {
        "name": current_project.get("name", "Без названия"),
        "customer": current_project.get("customer", {}),
        "description": project_description,
        "requirements": current_project.get("requirements", "Не определено"),
    }

    messages = list(state["messages"]) + [
        HumanMessage(
            f"""
            Тебе нужно подобрать услуги и опции на основе:
            - Требований: {state['project']['requirements']}
            - Описания проекта: {project_description}

            Если у тебя нет точной информации — **обязательно используй доступные инструменты** для получения данных из прайс-листа.
            Не придумывай данные. Сначала получи информацию, потом предложи варианты.
            ТВОЙ ОТВЕТ ДОЛЖЕН БЫТЬ НЕ СИЛЬНО ДЛИННЫМ, ИМЕННО ОТ РОЛИ КОНСУЛЬТАНТА - КЛИЕНТУ.
            """
        )
    ]
    print(updated_project)
    return {"messages": messages, "project": updated_project}


def parse_budget_node(state: SystemState) -> dict:
    budget_prompt = PromptTemplate(
        template="""Извлеки из сообщения пользователя и контекста только бюджет,
    которым располагает пользователь и сроки, которые он предоставляет.
    Верни в формате 'Бюджет n (руб.), время m (ч.)'
    Если что-то не указано - введи "Неограничено".

    Сообщение пользователя: {user_input}
    Контекст: {context}

    НЕ ДОБАВЛЯЙ НИКАКИХ КОММЕНТАРИЕВ.""",
        input_variables=["user_input", "context"],
    )

    user_input = get_last_human_message(state)
    messages = state["messages"]
    new_messages = messages + [HumanMessage(content=user_input)]

    try:
        chain = budget_prompt | llm_with_tools
        result = chain.invoke(
            {
                "user_input": user_input,
                "context": [state["messages"][0]] + state["messages"][-3:],
            }
        )

        updated_project = {
            **state["project"],
            "estimate": result.content.strip(),
        }
        new_messages = new_messages + [
            HumanMessage(
                f"""
                Тебе нужно провести анализ бюджета на основе:
                - Требований проекта: {state['project']['requirements']}
                - Бюджета клиента и сроки реализации: {result.content.strip()}

                Для этого **обязательно используй доступные инструменты**, чтобы получить актуальные данные из прайс-листа.
                Необходимый прайс-лист - первая часть требований (т.е одно из: "Создание корпоративного сайта", "Создание интернет-магазина", "Создание простого лендинга",)
                Не давай рекомендаций и не сравнивай бюджет, пока не получишь точную информацию через инструменты.
                Если данные получены — кратко предложи клиенту компромисс (альтернативы, изменение сроков или бюджета).
                Отвечай от лица консультанта, коротко и по делу.
                """
            )
        ]

        return {"messages": new_messages, "project": updated_project}

    except Exception as e:
        print(f"Ошибка парсинга бюджета: {e}")
        new_messages = new_messages + [
            HumanMessage(
                f"""
                Тебе нужно провести анализ бюджета на основе:
                - Требований проекта: {state['project']['requirements']}
                - Неограниченного бюджета и сроков.

                Для этого **обязательно используй доступные инструменты**, чтобы получить актуальные данные из прайс-листа.
                Необходимый прайс-лист - первая часть требований (т.е одно из: "Создание корпоративного сайта", "Создание интернет-магазина", "Создание простого лендинга",)
                Не давай рекомендаций и не сравнивай бюджет, пока не получишь точную информацию через инструменты.
                Если данные получены — кратко предложи клиенту компромисс (альтернативы, изменение сроков или бюджета).
                Отвечай от лица консультанта, коротко и по делу.
                """
            )
        ]
        updated_project = {**state["project"], "estimate": "Не указан"}

        return {"messages": new_messages, "project": updated_project}


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
        chain = budget_analysis_prompt | simple_llm | budget_analysis_parser
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


def parse_middleware_node(state: SystemState) -> dict:
    message_sense_parser = JsonOutputParser(pydantic_object=UserBudgetSufficiency)
    message_sense_prompt = PromptTemplate(
        template="""Ты — строгий парсер. Твоя задача — проанализировать сообщение пользователя и контекст и 
        представить его в формате.
    {format_instructions}

    Сообщение: {user_input}
    Контекст: {context}

    НЕ ДОБАВЛЯЙ НИКАКИХ КОММЕНТАРИЕВ. ВЕРНИ ТОЛЬКО JSON.""",
        input_variables=["user_input", "context"],
        partial_variables={
            "format_instructions": message_sense_parser.get_format_instructions()
        },
    )

    try:
        chain = message_sense_prompt | simple_llm | message_sense_parser
        result = chain.invoke(
            {
                "user_input": state["messages"][-1].content,
                "context": state["messages"][-3:],
            }
        )

        if isinstance(result, str):
            result_lower = result.strip().lower()
            if "true" in result_lower or "да" in result_lower:
                sense = True
            else:
                sense = False
        else:
            sense = result.get("state", False)

    except Exception as e:
        print(f"Ошибка парсинга анализа бюджета: {e}")
        sense = True

    return {"should_continue": sense}
