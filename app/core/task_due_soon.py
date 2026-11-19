from datetime import datetime, timedelta, timezone
from typing import Optional
from app.models.task import StatusEnum

DUE_SOON_DAYS = 3


def is_task_due_soon(
    due_date: Optional[datetime],
    status: Optional[str],
    now: Optional[datetime] = None,
    days: int = DUE_SOON_DAYS,
) -> bool:
    """
    Kiểm tra bài tập có sắp đến hạn hay không:
    - Có due_date
    - Trạng thái khác DONE
    - Thời hạn nằm trong khoảng từ hiện tại (now) đến (now + days ngày)
    """
    if due_date is None:
        return False

    current_status = (status or "").strip().upper()
    if current_status == StatusEnum.DONE.value:
        return False

    current_time = now if now is not None else datetime.now(timezone.utc)

    if due_date.tzinfo is None and current_time.tzinfo is not None:
        current_time = current_time.replace(tzinfo=None)
    elif due_date.tzinfo is not None and current_time.tzinfo is None:
        due_date = due_date.replace(tzinfo=None)

    deadline_limit = current_time + timedelta(days=days)
    return current_time <= due_date <= deadline_limit