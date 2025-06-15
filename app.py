import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.database.config import init_db, engine
from src.routers.destination import router
# from src.routers.main import app
# from src.routers.user_location import user_loc
from src.routers.trips import trips_route

main_app = FastAPI()
Instrumentator().instrument(main_app).expose(main_app)


main_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app.include_router(router)
main_app.include_router(trips_route)



@main_app.on_event("startup")
async def app_startup():
    init_db(engine=engine)



if __name__ == "__main__":
    uvicorn.run("app:main_app", port=8000, reload=True)