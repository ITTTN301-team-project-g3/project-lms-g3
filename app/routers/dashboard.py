from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.subject import Subject
from app.models.task import Task, StatusEnum
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


class DashboardStatsResponse(BaseModel):
    total_subjects: int
    total_tasks: int
    todo_tasks: int
    in_progress_tasks: int
    done_tasks: int
    completion_rate: float


@router.get("/stats", response_model=DashboardStatsResponse, summary="Thống kê tổng quan cho Dashboard")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_subjects = db.query(Subject).filter(Subject.user_id == current_user.id).count()

    base_task_query = db.query(Task).join(Subject).filter(Subject.user_id == current_user.id)

    total_tasks = base_task_query.count()
    todo_tasks = base_task_query.filter(Task.status == StatusEnum.TODO).count()
    in_progress_tasks = base_task_query.filter(Task.status == StatusEnum.IN_PROGRESS).count()
    done_tasks = base_task_query.filter(Task.status == StatusEnum.DONE).count()

    completion_rate = round((done_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0.0

    return DashboardStatsResponse(
        total_subjects=total_subjects,
        total_tasks=total_tasks,
        todo_tasks=todo_tasks,
        in_progress_tasks=in_progress_tasks,
        done_tasks=done_tasks,
        completion_rate=completion_rate
    )