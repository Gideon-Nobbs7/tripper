import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers.main import app
from src.routers.user_location import user_loc


main_app = FastAPI()


main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app.include_router(app)
main_app.include_router(user_loc)


if __name__ == "__main__":
    uvicorn.run("app:main_app", port=8000, reload=True)