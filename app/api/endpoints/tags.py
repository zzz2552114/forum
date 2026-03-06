from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from app.schemas.tag import TagCreate, TagResponse
from app.schemas.common import ResponseBase, PaginationData
from app.core.responses import success_response, paginate_response
from app.models.tag import Tag
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.enums import UserRole

router = APIRouter()

@router.get("/", response_model=ResponseBase[PaginationData[TagResponse]])
async def read_tags(keyword: Optional[str] = None, page: int = 1, page_size: int = 20):
    query = Tag.all()
    if keyword:
        query = query.filter(name__icontains=keyword)
        
    total = await query.count()
    skip = (page - 1) * page_size
    tags = await query.offset(skip).limit(page_size)
    
    return paginate_response(tags, page, page_size, total)

@router.post("/", response_model=ResponseBase[TagResponse])
async def create_tag(tag_in: TagCreate, current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.MASTER, UserRole.ADMIN, UserRole.SUPER_ROOT]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    exists = await Tag.get_or_none(name=tag_in.name)
    if exists:
        raise HTTPException(status_code=400, detail="Tag already exists")
        
    tag = await Tag.create(**tag_in.model_dump())
    return success_response(tag)

@router.patch("/{tag_id}", response_model=ResponseBase[TagResponse])
async def update_tag(tag_id: int, tag_in: TagCreate, current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.MASTER, UserRole.ADMIN, UserRole.SUPER_ROOT]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
        
    tag.name = tag_in.name
    if tag_in.slug:
        tag.slug = tag_in.slug
    await tag.save()
    return success_response(tag)

@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, current_user: User = Depends(get_current_active_user)):
    if current_user.role not in [UserRole.MASTER, UserRole.ADMIN, UserRole.SUPER_ROOT]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    deleted = await Tag.filter(id=tag_id).delete()
    if not deleted:
        raise HTTPException(status_code=404, detail="Tag not found")
    return success_response({"message": "Tag deleted"})
