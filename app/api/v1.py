from fastapi import APIRouter

from app.auth.routers.auth import router as auth_router
from app.auth.routers.user import router as user_router
from app.trigger.routers.task import router as task_router
from app.trigger.routers.trigger import router as trigger_router

router = APIRouter(
    prefix="/api/v1",
)

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(trigger_router)
router.include_router(task_router)
