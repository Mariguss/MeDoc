import uvicorn

from app.core.config import settings
from app.core.server import app


@app.get("/")
async def root():
    return {"message": "Hello World, go to /docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.run.host, port=settings.run.port, reload=True)
