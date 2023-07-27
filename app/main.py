import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api import v1
from app.config import settings
from app.utils.db import setup_db
from app.utils.exception_handler import setup_exception_handler
from app.utils.logger import setup_logger

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.mount(
    "/static",
    StaticFiles(directory=settings.BASE_DIR + "/statics"),
    name="static",
)

if settings.BACKEND_CORS_ORIGINS:
    allow_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(v1.router)

# register exception handlers
setup_exception_handler(app)
# logger
logger = setup_logger(settings.PROJECT_NAME, debug_sql=settings.DEBUG_sql)
# db
setup_db(
    app,
    db_url=settings.DATABASE_URL,
    modules={"models": settings.APPLICATION_MODULES},
)


@app.on_event("startup")
async def startup() -> None:
    if settings.REDIS_TESTING:
        return


@app.on_event("shutdown")
async def shutdown() -> None:
    if settings.REDIS_TESTING:
        return


def run_app():
    uvicorn.run(app, host="0.0.0.0", port=8000)
