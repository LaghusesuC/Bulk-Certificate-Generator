
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.api.jobs import router as jobs_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Bulk Certificate Generator API",
    lifespan=lifespan,
)


app.include_router(jobs_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
