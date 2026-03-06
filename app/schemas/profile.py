from typing import Optional
from pydantic import BaseModel, HttpUrl
from datetime import datetime

from app.models.enums import UserRole, TrustLevel, SchoolVisibility

class UserProfileBase(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    school_name: Optional[str] = None

class UserPrivacyUpdate(BaseModel):
    school_visibility: Optional[SchoolVisibility] = None
    # Can extend with allow_anonymous_post etc later

class UserProfileResponse(UserProfileBase):
    id: int
    username: str
    email: str
    school_visibility: SchoolVisibility
    role: UserRole
    trust_level: TrustLevel
    reputation_score: int
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

class UserPublicProfileResponse(BaseModel):
    id: int
    username: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    school_name: Optional[str] = None
    school_visibility: SchoolVisibility
    trust_level: TrustLevel
    reputation_score: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
