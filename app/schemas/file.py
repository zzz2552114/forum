from pydantic import BaseModel, ConfigDict
from datetime import datetime

class FileResponse(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    url: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
