from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.lms import router as lms_router
from app.api.routes.visit import router as visit_router
from app.core.config import settings
from app.db.bootstrap import ensure_schema


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_schema()
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.include_router(health_router)
app.include_router(lms_router, prefix=settings.api_prefix)
app.include_router(visit_router, prefix=settings.api_prefix)
