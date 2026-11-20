from typing import Any, Optional
from pydantic import BaseModel

class StandardResponse(BaseModel):
    success: bool = True
    message: str = "Thành công"
    data: Optional[Any] = None