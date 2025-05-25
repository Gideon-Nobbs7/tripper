import uvicorn
from fastapi import FastAPI
from src.routers.main import app


main_app = FastAPI()

main_app.include_router(app)


if __name__ == "__main__":
    uvicorn.run("app:main_app", port=8000, reload=True)