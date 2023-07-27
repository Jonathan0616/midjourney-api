from fastapi import APIRouter

from app.trigger.schemas.task import Task
from app.trigger.services.task import task_service
from app.utils.json import json_response
from app.utils.response import Response

router = APIRouter(
    prefix="/task",
    tags=["task"],
)


@router.get(
    "/{task_id}",
    response_model=Response[Task],
    summary="Query task details",
)
async def details(task_id: str):
    data = task_service.details(task_id)
    return json_response(data=data)
