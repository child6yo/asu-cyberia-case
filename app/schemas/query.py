from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    chat_id: str


class QueryResponse(BaseModel):
    chat_id: str