import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from src.database.config import engine, init_db
from src.routers import destination, trips


app = FastAPI(
    title="Tripper API",
    description="API for managing trips and their destinations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

Instrumentator().instrument(app).expose(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(destination.router, prefix="/api/v1")
app.include_router(trips.router, prefix="/api/v1")



@app.on_event("startup")
async def app_startup():
    init_db(engine=engine)


@app.get("/api/v1/healthcheck", tags=["Monitoring"])
async def healthcheck():
    return {"status": "ok", "message": "Tripper API is running"}



if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)