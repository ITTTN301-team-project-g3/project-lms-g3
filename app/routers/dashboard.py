from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.subject import Subject
from app.models.task import StatusEnum, Task
from app.models.user import User

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
    total_subjects = (
        db.query(func.count(Subject.id))
        .filter(Subject.user_id == current_user.id)
        .scalar()
        or 0
    )

    # Gom toàn bộ thống kê trạng thái bài tập vào 1 truy vấn SQL duy nhất (tối ưu NFR-07)
    stats_row = (
        db.query(
            func.count(Task.id).label("total"),
            func.sum(case((Task.status == StatusEnum.TODO, 1), else_=0)).label("todo"),
            func.sum(case((Task.status == StatusEnum.IN_PROGRESS, 1), else_=0)).label("in_progress"),
            func.sum(case((Task.status == StatusEnum.DONE, 1), else_=0)).label("done"),
        )
        .join(Subject)
        .filter(Subject.user_id == current_user.id)
        .first()
    )

    total_tasks = int(stats_row.total or 0) if stats_row else 0
    todo_tasks = int(stats_row.todo or 0) if stats_row else 0
    in_progress_tasks = int(stats_row.in_progress or 0) if stats_row else 0
    done_tasks = int(stats_row.done or 0) if stats_row else 0

    completion_rate = round((done_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0.0

    return DashboardStatsResponse(
        total_subjects=total_subjects,
        total_tasks=total_tasks,
        todo_tasks=todo_tasks,
        in_progress_tasks=in_progress_tasks,
        done_tasks=done_tasks,
        completion_rate=completion_rate
    )