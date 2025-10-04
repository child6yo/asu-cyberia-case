from fastapi import FastAPI
import uvicorn

from routes.router import router

app = FastAPI(
    title="Chat API",
    version="0.1.0",
    description="Бэкенд чата",
)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=False)
