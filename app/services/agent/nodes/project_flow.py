from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from services.agent.models.models import *
from services.agent.llm.client import *
from services.agent.utils.messages import get_last_human_message

project_types = [
    "Создание корпоративного сайта",
    "Создание интернет-магазина",
    "Создание простого лендинга",
]


def project_type_node(state: SystemState) -> dict:
    try:
        messages = state["messages"] + [
            HumanMessage(
                content=f"Теперь необходимо спросить о типе проекта... Возможные типы: {', '.join(project_types)}."
            )
        ]
        response = simple_llm.invoke(messages)
        new_messages = messages + [AIMessage(content=response.content)]
        return {"messages": new_messages}
    except Exception as e:
        return {
            "messages": state["messages"] + [AIMessage(content="Извините, ошибка...")]
        }


def detalize_node(state: SystemState) -> dict:
    messages = list(state["messages"]) + [
        HumanMessage(
            f"""
            Проанализируй прайс-лист, исходя из требования {state['project']['requirements']},
            Озвучь требуемые услуги и предложи дополнительные опции, которые подошли бы
            по описанию {state['project']['description']}.

            Спроси пользователя, верно ли все озвучено. Если что-то не верно — пользователь должен объяснить.
            ТВОЙ ОТВЕТ ДОЛЖЕН БЫТЬ НЕ СИЛЬНО ДЛИННЫМ, ИМЕННО ОТ РОЛИ КОНСУЛЬТАНТА - КЛИЕНТУ.
            """
        )
    ]
    response = llm_with_tools.invoke([messages[0]] + messages[-3:])
    print(response.content)

    return {"messages": state["messages"] + [response]}


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

    try:
        chain = agreement_prompt | llm_with_tools | agreement_parser
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

    return {"should_continue": agreement}


def correcting_node(state: SystemState) -> dict:
    user_input = get_last_human_message(state)

    correction_prompt = PromptTemplate(
        template="""Пользователь указал, что в предыдущих требованиях к проекту есть ошибки.
        На основе его комментария извлеки обновлённые требования к проекту.

        Контекст: {context}
        Текущие требования: {requirements}
        Текущее описание: {description}
        Комментарий пользователя: {user_input}

        Обновленные требования НЕОБХОДИМО ИЗВЛЕЧЬ В ФОРМАТЕ ПРЕДЫДУЩИХ ТРЕБОВАНИЙ.
        
        НЕ ДОБАВЛЯЙ НИКАКИХ КОММЕНТАРИЕВ.""",
        input_variables=["context", "requirements", "description", "user_input"],
    )

    try:
        chain = correction_prompt | llm_with_tools
        updated_requirements = chain.invoke(
            {
                "context": [state["messages"][0]] + state["messages"][-3:],
                "user_input": user_input,
                "requirements": state["project"]["requirements"],
                "description": state["project"]["description"],
            }
        )

        new_req = updated_requirements.content.strip()
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

        response = simple_llm.invoke([messages[0]] + messages[-3:])
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


def budget_analysis_node(state: SystemState) -> dict:
    messages = list(state["messages"]) + [
        HumanMessage(
            f"""
            Проанализируй прайс-лист, исходя из требований: {state['project']['requirements']},
            сопоставь с бюджетом пользователя и требованиями по времени - {state['project']['estimate']} и

            Если что-то не вписывается в рамки - предложи альтернативы, либо предложи пользователю увеличить сроки/бюджет.
            Иными словами, если запросы пользователя не вписываются в прайс-лист - предложи компромисс.

            ТВОЙ ОТВЕТ ДОЛЖЕН БЫТЬ НЕ СИЛЬНО ДЛИННЫМ, ИМЕННО ОТ РОЛИ КОНСУЛЬТАНТА - КЛИЕНТУ.
            """
        )
    ]
    response = llm_with_tools.invoke([messages[0]] + messages[-3:])
    print(response.content)

    return {"messages": [response]}


def budget_correcting_node(state: SystemState) -> dict:
    user_input = get_last_human_message(state)
    messages = state["messages"]
    new_messages = messages + [HumanMessage(content=user_input)]

    try:
        response = simple_llm.invoke([messages[0]] + new_messages[-3:])
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


def mid_node(state: SystemState) -> dict:
    return {}
