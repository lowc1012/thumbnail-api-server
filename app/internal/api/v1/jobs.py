from http import HTTPStatus

from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.internal.tasks.celery import celery_app

router = APIRouter()


class JobResponse(BaseModel):
    job_id: str = Field(description="Job identifier")
    status: str = Field(description="Job status")
    thumbnail_url: str | None = Field(default=None, description="Thumbnail URL if completed")


@router.get("/jobs/{job_id}")
def get_job(job_id: str) -> JobResponse:
    task = AsyncResult(job_id, app=celery_app)

    if task.state == "PENDING":
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Job not found")

    if task.state == "SUCCESS":
        result = task.result
        return JobResponse(
            job_id=job_id,
            status=task.state.lower(),
            thumbnail_url=result.get("thumbnail_url")
        )

    return JobResponse(job_id=job_id, status=task.state.lower())


@router.get("/jobs/")
def list():
    # TODO
    pass


@router.get("/jobs/{job_id}/thumbnail")
def get_thumbnail_by_job_id(job_id: str):
    # TODO
    pass
