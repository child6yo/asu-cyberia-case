from pydantic import BaseModel, Field
from typing import TypedDict, Optional, Annotated, List, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

project_types = [
    "Создание корпоративного сайта",
    "Создание интернет-магазина",
    "Создание простого лендинга",
]


class MessageSense(BaseMessage):
    sense: bool = Field(
        description="""Имеет ли сообщение смысл в контексте диалога. 
        True - если сообщение вписывается в контекст и не требует ответа на НЕ ПОСТАВЛЕННЫЙ РАНЕЕ В КОНТЕКСТЕ вопрос. 
        False - если требуется что-то уточнить, сообщение является вопросом, или же не вписывается в контекст."""
    )


class UserAgreement(BaseModel):
    is_user_agree: bool = Field(
        description="Согласен ли пользователь с тем, что все верно"
    )


class UserBudgetSufficiency(BaseModel):
    state: bool = Field(
        description="Хватает ли пользователю бюджета или адекватные ли сроки он предоставил."
    )


class Customer(BaseModel):
    name: Optional[str] = Field(None, description="Имя заказчика")
    email: Optional[str] = Field(None, description="Электронная почта заказчика")
    phone: Optional[str] = Field(None, description="Номер телефона заказчика")


class Project(TypedDict):
    name: str
    customer: Customer
    description: str
    requirements: str
    estimate: str


class SystemState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    project: Project
    should_continue: bool
