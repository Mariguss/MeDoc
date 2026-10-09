import uvicorn

from app.core.server import app


@app.get("/")
async def root():
    return {"message": "Hello World, go to /docs"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.5", port=8005, reload=True)
