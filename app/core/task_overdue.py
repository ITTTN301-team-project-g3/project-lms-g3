from datetime import datetime, timezone
from typing import Optional
from app.models.task import StatusEnum


def is_task_overdue(
    due_date: Optional[datetime],
    status: Optional[str],
    now: Optional[datetime] = None,
) -> bool:
    """
    Kiểm tra bài tập có quá hạn hay không:
    - Có due_date
    - Trạng thái khác DONE
    - due_date < thời điểm hiện tại
    """
    if due_date is None:
        return False

    current_status = (status or "").strip().upper()
    if current_status == StatusEnum.DONE.value:
        return False

    current_time = now if now is not None else datetime.now(timezone.utc)

    # Tránh lỗi lệch aware / naive datetime khi so sánh
    if due_date.tzinfo is None and current_time.tzinfo is not None:
        current_time = current_time.replace(tzinfo=None)
    elif due_date.tzinfo is not None and current_time.tzinfo is None:
        due_date = due_date.replace(tzinfo=None)

    return due_date < current_time