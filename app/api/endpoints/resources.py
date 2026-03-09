from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.schemas.resource import ResourceCreate, ResourceResponse, ResourceVersionResponse
from app.schemas.common import ResponseBase, PaginationData
from app.core.responses import success_response, paginate_response
from app.models.resource import Resource, ResourceVersion
from app.models.file import File
from app.models.category import Space
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()
from app.models.enums import ContentStatus

@router.get("/", response_model=ResponseBase[PaginationData[ResourceResponse]])
async def read_resources(
    space_id: Optional[int] = None, 
    resource_type: Optional[str] = None,
    page: int = 1, 
    page_size: int = 20
):
    query = Resource.filter(status=ContentStatus.PUBLISHED)
    if space_id:
        from tortoise.expressions import Q
        query = query.filter(Q(space_id=space_id) | Q(school_space_id=space_id))
    if resource_type:
        query = query.filter(resource_type=resource_type)
        
    total = await query.count()
    skip = (page - 1) * page_size
    resources = await query.offset(skip).limit(page_size).prefetch_related("uploader", "space", "versions")
    
    response_items = []
    for r in resources:
        versions = [ResourceVersionResponse.model_validate(v) for v in r.versions]
        response_items.append(ResourceResponse(
            id=r.id,
            title=r.title,
            description=r.description,
            resource_type=r.resource_type,
            school_space_id=r.school_space_id,
            space_id=r.space.id,
            filename=r.filename,
            uploader_id=r.uploader.id,
            download_count=r.download_count,
            bookmark_count=r.bookmark_count,
            created_at=r.created_at,
            versions=versions
        ))
        
    return paginate_response(response_items, page, page_size, total)

@router.post("/", response_model=ResponseBase[ResourceResponse])
async def create_resource(resource_in: ResourceCreate, current_user: User = Depends(get_current_active_user)):
    space = await Space.get_or_none(id=resource_in.space_id)
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
        
    file = await File.get_or_none(id=resource_in.file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
        
    resource = await Resource.create(
        title=resource_in.title,
        description=resource_in.description,
        resource_type=resource_in.resource_type,
        school_space_id=resource_in.school_space_id,
        space_id=space.id,
        uploader_id=current_user.id,
        filename=file.filename
    )
    
    version = await ResourceVersion.create(
        resource=resource,
        file=file,
        version_note=resource_in.version_note
    )
    
    await resource.fetch_related("uploader", "space", "versions")
    
    return success_response(ResourceResponse(
        id=resource.id,
        title=resource.title,
        description=resource.description,
        resource_type=resource.resource_type,
        school_space_id=resource.school_space_id,
        space_id=resource.space_id,
        filename=resource.filename,
        uploader_id=resource.uploader_id,
        download_count=resource.download_count,
        bookmark_count=resource.bookmark_count,
        created_at=resource.created_at,
        versions=[ResourceVersionResponse.model_validate(version)]
    ))

@router.get("/{resource_id}", response_model=ResponseBase[ResourceResponse])
async def read_resource(resource_id: int):
    resource = await Resource.get_or_none(id=resource_id).prefetch_related("uploader", "space", "versions")
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    versions = [ResourceVersionResponse.model_validate(v) for v in resource.versions]
    return success_response(ResourceResponse(
        id=resource.id,
        title=resource.title,
        description=resource.description,
        resource_type=resource.resource_type,
        school_space_id=resource.school_space_id,
        space_id=resource.space.id,
        filename=resource.filename,
        uploader_id=resource.uploader.id,
        download_count=resource.download_count,
        bookmark_count=resource.bookmark_count,
        created_at=resource.created_at,
        versions=versions
    ))
