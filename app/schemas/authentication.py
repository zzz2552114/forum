from pydantic import BaseModel, EmailStr
from typing import Optional

class StuAuthRequest(BaseModel):
    email: EmailStr
    school_name: str

class StuAuthVerify(BaseModel):
    code: str

class StuAuthResponse(BaseModel):
    success: bool
    message: str
    sent_to: Optional[str] = None
    code: Optional[str] = None
