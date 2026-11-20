from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.task import Task, StatusEnum
from app.models.subject import Subject

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", summary="Thống kê và cảnh báo Dashboard")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now = datetime.now()
    next_week = now + timedelta(days=7)

    tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
    subjects_count = db.query(Subject).filter(
        Subject.user_id == current_user.id
    ).count()

    overdue = [
        task for task in tasks
        if task.due_date is not None
        and task.due_date < now
        and task.status != StatusEnum.DONE.value
    ]

    upcoming = [
        task for task in tasks
        if task.due_date is not None
        and now <= task.due_date <= next_week
        and task.status != StatusEnum.DONE.value
    ]

    subject_names = {
        subject.id: subject.name
        for subject in db.query(Subject).filter(
            Subject.user_id == current_user.id
        ).all()
    }

    def task_item(task):
        return {
            "id": task.id,
            "title": task.title,
            "subject_name": subject_names.get(task.subject_id, "Không xác định"),
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "status": task.status
        }

    return {
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email
        },
        "total_subjects": subjects_count,
        "total_tasks": len(tasks),
        "todo_tasks": sum(1 for task in tasks if task.status == StatusEnum.TODO.value),
        "in_progress_tasks": sum(1 for task in tasks if task.status == StatusEnum.IN_PROGRESS.value),
        "done_tasks": sum(1 for task in tasks if task.status == StatusEnum.DONE.value),
        "overdue_count": len(overdue),
        "upcoming_count": len(upcoming),
        "overdue_tasks": [task_item(task) for task in sorted(overdue, key=lambda item: item.due_date)[:5]],
        "upcoming_tasks": [task_item(task) for task in sorted(upcoming, key=lambda item: item.due_date)[:5]]
    }
