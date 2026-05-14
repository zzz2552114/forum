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
import aiofiles
from PIL import Image

# Local testing flag to bypass strict role requirements
ENABLE_LOCAL_TESTING = os.getenv("ENABLE_LOCAL_TESTING", "true").lower() == "true"

router = APIRouter()
UPLOAD_DIR = "uploads"
AVATAR_DIR = os.path.join(UPLOAD_DIR, "avatars")
GENERAL_DIR = os.path.join(UPLOAD_DIR, "general")

# Ensure upload directories exist
os.makedirs(AVATAR_DIR, exist_ok=True)
os.makedirs(GENERAL_DIR, exist_ok=True)

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
    file_path = os.path.join(GENERAL_DIR, unique_filename)
    
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                await buffer.write(chunk)
                
        if file.content_type and file.content_type.startswith("image/"):
            try:
                with Image.open(file_path) as img:
                    img.verify()
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid image file format")
                
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
        
    file_size = os.path.getsize(file_path)
    
    # In a real app, url would be a proper domain/path
    url = f"/static/uploads/general/{unique_filename}"
    
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
# 上传头像 (任何基础以上等级用户可用)
# ==========================================
@router.post("/avatar", response_model=ResponseBase[FileResponse])
async def upload_avatar(
    file: UploadFile = FastAPIFile(...),
    current_user: User = Depends(get_current_active_user)
):
    """
        此函数用于上传头像,只有基础以上等级用户可用
    """
    if not ENABLE_LOCAL_TESTING:
        # TrustLevel 1 (BASIC) 或以上即可上传头像
        if current_user.trust_level < 1 and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ROOT]:
            raise HTTPException(status_code=403, detail="Login required to upload avatar")
            
    # 限制必须是图片类型
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed for avatars")
        
    file_ext = os.path.splitext(file.filename)[1]
    if not file_ext:
        file_ext = ".png" # fallback extension
        
    unique_filename = f"avatar_{uuid.uuid4().hex}{file_ext}"
    file_path = os.path.join(AVATAR_DIR, unique_filename)
    
    try:
        async with aiofiles.open(file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                await buffer.write(chunk)
                
        try:
            with Image.open(file_path) as img:
                img.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid image file format")
            
    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Avatar upload failed: {str(e)}")
        
    file_size = os.path.getsize(file_path)
    url = f"/static/uploads/avatars/{unique_filename}"
    
    db_file = await File.create(
        filename=file.filename,
        content_type=file.content_type,
        size=file_size,
        url=url,
        biz_type="avatar",
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
