from pydantic import BaseModel, Field
from typing import TypedDict, Optional, Annotated, List, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

project_types = [
    "Создание корпоративного сайта",
    "Создание интернет-магазина",
    "Создание простого лендинга",
]

class UserAgreement(BaseModel):
    is_user_agree: bool = Field(description="Согласен ли пользователь с тем, что все верно.")


class Customer(BaseModel):
    name: Optional[str] = Field(None, description="Имя заказчика")
    email: Optional[str] = Field(None, description="Электронная почта заказчика")
    phone: Optional[str] = Field(None, description="Номер телефона заказчика")


class Requirements(BaseModel):
    type: Optional[str] = Field(
        description="Тип проекта: Создание корпоративного сайта, Создание интернет-магазина, Создание простого лендинга"
    )
    options: Optional[List[str]] = Field(
        description="Опциональные параметры к проекту: все, что пользователь пожелает."
    )


class Project(TypedDict):
    name: str
    customer: Customer
    description: str
    requirements: Requirements

class SystemState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    project: Project
    should_continue: bool