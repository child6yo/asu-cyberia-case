from pydantic import BaseModel, Field
from typing import List


class Option(BaseModel):
    name: str = Field(description="Название опции (например, 'Адаптивная верстка')")
    term: int = Field(description="Срок выполнения опции в рабочих днях", ge=0)
    price: float = Field(description="Стоимость опции в рублях", ge=0.0)


class Options(BaseModel):
    options: List[Option] = Field(description="Список доступных опций для услуги")

