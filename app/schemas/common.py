from typing import TypeVar, Generic, Optional, List, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class PaginationData(BaseModel, Generic[T]):
    items: List[T]
    pagination: dict = Field(
        ..., 
        description="分页信息",
        json_schema_extra={
            "example": {
                "page": 1,
                "page_size": 20,
                "total": 100,
                "has_next": True
            }
        }
    )

class ResponseBase(BaseModel, Generic[T]):
    code: int = Field(default=0, description="状态码, 0 为成功")
    message: str = Field(default="ok", description="响应信息")
    data: Optional[T] = Field(default=None, description="响应数据")
