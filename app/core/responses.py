from typing import Any, Optional

def success_response(data: Optional[Any] = None, message: str = "ok") -> dict:
    """统一成功响应"""
    return {
        "code": 0,
        "message": message,
        "data": data if data is not None else {}
    }

def error_response(code: int, message: str, data: Optional[Any] = None) -> dict:
    """统一错误响应"""
    return {
        "code": code,
        "message": message,
        "data": data
    }

def paginate_response(items: list, page: int, page_size: int, total: int) -> dict:
    """构建分页响应体"""
    return success_response({
        "items": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "has_next": (page * page_size) < total
        }
    })
