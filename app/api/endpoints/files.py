from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, Form, HTTPException
from app.schemas.file import FileResponse
from app.schemas.common import ResponseBase
from app.core.responses import success_response
from app.models.file import File
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.enums import UserRole
import os
import uuid
import shutil

# Local testing flag to bypass strict role requirements
ENABLE_LOCAL_TESTING = os.getenv("ENABLE_LOCAL_TESTING", "true").lower() == "true"

router = APIRouter()
UPLOAD_DIR = "uploads"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==========================================
# 上传文件 (依赖当前用户的信任等级)
# ==========================================
@router.post("/", response_model=ResponseBase[FileResponse])
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    biz_type: str = Form(None),
    current_user: User = Depends(get_current_active_user)
):
    if not ENABLE_LOCAL_TESTING:
        if current_user.trust_level < 2 and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ROOT]:
            raise HTTPException(status_code=403, detail="Trust level 2 required to upload files")
        
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    file_size = os.path.getsize(file_path)
    
    # In a real app, url would be a proper domain/path
    url = f"/static/uploads/{unique_filename}"
    
    db_file = await File.create(
        filename=file.filename,
        content_type=file.content_type,
        size=file_size,
        url=url,
        biz_type=biz_type,
        uploader=current_user
    )
    
    return success_response(db_file)

# ==========================================
# 获取文件信息
# ==========================================
@router.get("/{file_id}", response_model=ResponseBase[FileResponse])
async def read_file(file_id: int):
    db_file = await File.get_or_none(id=file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return success_response(db_file)

# ==========================================
# 删除文件 (只能删除自己的，或者管理员删除任何文件)
# ==========================================
@router.delete("/{file_id}")
async def delete_file(file_id: int, current_user: User = Depends(get_current_active_user)):
    db_file = await File.get_or_none(id=file_id).prefetch_related("uploader")
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
        
    if db_file.uploader.id != current_user.id and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ROOT]:
        raise HTTPException(status_code=403, detail="Not permitted to delete this file")
        
    # Physically remove if file exists locally
    local_path = db_file.url.replace("/static/", "")
    if os.path.exists(local_path):
        os.remove(local_path)
        
    await db_file.delete()
    return success_response({"message": "File deleted"})
