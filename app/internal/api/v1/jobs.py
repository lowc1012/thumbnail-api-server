from http import HTTPStatus
import json
from typing import List

from celery.backends.database.models import Task
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.internal.dependencies import get_db_session, get_storage_service
from app.internal.services.storage import StorageService

router = APIRouter()


class JobResponse(BaseModel):
    job_id: str = Field(description="Job identifier")
    status: str = Field(description="Job status")
    result: str | None = Field(default=None, description="Job result")


class ThumbnailUrlResponse(BaseModel):
    job_id: str = Field(description="Job identifier")
    thumbnail_url: str = Field(description="Presigned URL to download thumbnail")


@router.get("/jobs/{job_id}")
def get_job(job_id: str, session: Session = Depends(get_db_session)) -> JobResponse:
    statement = select(Task).where(Task.task_id == job_id)
    task = session.exec(statement).first()
    if task is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Job not found")

    return JobResponse(
        job_id=job_id,
        status=task.status,
        result=json.dumps(task.result),
    )


@router.get("/jobs/")
def list_jobs(session: Session = Depends(get_db_session)) -> List[JobResponse]:
    """List all submitted jobs"""
    statement = select(Task)
    jobs = session.exec(statement).all()
    res = []
    for job in jobs:
        res.append(
            JobResponse(
                job_id=job.task_id,
                status=job.status,
                result=json.dumps(job.result),
            )
        )
    return res


@router.get("/jobs/{job_id}/thumbnail")
def get_thumbnail_by_job_id(
    job_id: str,
    session: Session = Depends(get_db_session),
    storage_service: StorageService = Depends(get_storage_service)
) -> ThumbnailUrlResponse:
    """Get presigned URL for thumbnail download"""
    statement = select(Task).where(Task.task_id == job_id)
    task = session.exec(statement).first()
    
    if task is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Job not found")
    
    if task.status != "SUCCESS":
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Job status: {task.status}")
    
    result = json.loads(task.result)
    thumbnail_key = result.get("key")
    presigned_url = storage_service.generate_presigned_url(thumbnail_key)
    
    return ThumbnailUrlResponse(job_id=job_id, thumbnail_url=presigned_url)
