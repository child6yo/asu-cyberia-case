from fastapi import FastAPI
import uvicorn

from routes.query import router

app = FastAPI(title="Chat API", version="0.1.0", description="Тестовый бэкенд для интеграции с фронтом")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "API работает. Используйте /api/query?chat_id=value"}

if __name__ == '__main__':
    uvicorn.run("main:app", reload=True)