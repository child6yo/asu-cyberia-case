from fastapi import FastAPI
import uvicorn

from routes.chat import router

app = FastAPI(
    title="Chat API",
    version="0.1.0",
    description="Тестовый бэкенд для интеграции с фронтом",
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=False)
