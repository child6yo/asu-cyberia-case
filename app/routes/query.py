from fastapi import APIRouter, HTTPException, Query
from schemas.query import QueryRequest, QueryResponse

router = APIRouter(prefix="/api", tags=["query"])


@router.get("/query", response_model=QueryResponse)
async def get_query(chat_id: str = Query(..., description="ID чата")):
    """
    Тестовый эндпоинт, возвращает переданный chat_id.
    Используется для проверки интеграции с фронтом.
    """
    if not chat_id.strip():
        raise HTTPException(status_code=400, detail="chat_id не может быть пустым")

    return QueryResponse(chat_id=chat_id)

