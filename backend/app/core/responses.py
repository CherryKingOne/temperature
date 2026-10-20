from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, model_validator

from app.core.context import get_request_id

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一响应信封。"""

    code: int = 0
    message: str = "success"
    data: T | None = None
    request_id: str | None = None

    @model_validator(mode="after")
    def _fill_request_id(self) -> "ApiResponse":
        if self.request_id is None:
            object.__setattr__(self, "request_id", get_request_id())
        return self
