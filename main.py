import uvicorn
from fastapi import FastAPI

from app.api.v1.routes import routers
from app.core.exceptions_handler import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)

app.include_router(routers)

@app.get("/")
async def root():
    return {"message": "Hello World, go to /docs"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.5",
        port=8005,
        reload=True
    )
