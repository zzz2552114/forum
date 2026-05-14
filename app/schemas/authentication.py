from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List

# authentication schemas

# 发入的验证请求，要求包含学校名称和邮箱
class StuAuthRequest(BaseModel):
    school_name: str = Field(..., description="学校名称")
    email: EmailStr = Field(..., description="教育邮箱")

# 填写的验证码
class StuAuthVerify(BaseModel):
    code: str = Field(..., min_length=6, max_length=6, description="6位验证码")

# 返回的结果，包含是否成功
class StuAuthResponse(BaseModel):
    success: bool
    message: str
    sent_to: Optional[str] = Field(default=None, description="发送到的邮箱 (测试期专用)")
    code: Optional[str] = Field(default=None, description="生成的验证码 (测试期专用)")