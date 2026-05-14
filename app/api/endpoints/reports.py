from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.models.report import Report
from app.models.enums import ReviewStatus, TrustLevel
from app.models.user import User
from app.api.deps import get_current_user, ensure_min_trust, ensure_admin_or_super_root
from app.schemas.common import ResponseBase
from app.schemas.report import ReportCreate, ReportResponse, ReportUpdate
from app.core.responses import success_response

router = APIRouter()

# ==========================================
# 提交举报 (必须登录，且trust_level >= 1)
# ==========================================
@router.post("/", response_model=ResponseBase[ReportResponse])
async def create_report(report_in: ReportCreate, current_user: User = Depends(get_current_user)):
    """
    这个函数是用来发送举报请求的,只有登录用户可以举报
    """
    ensure_min_trust(
        current_user, 
        min_level=TrustLevel.BASIC, 
        required_permission="report.create"
    )
    
    if not report_in.post_id and not report_in.comment_id:
        raise HTTPException(status_code=400, detail="必须提供帖子ID或评论ID")
        
    report = await Report.create(
        reporter_id=current_user.id,
        reason=report_in.reason,
        post_id=report_in.post_id,
        comment_id=report_in.comment_id,
        status=ReviewStatus.PENDING.value
    )
    return success_response(report)


# ==========================================
# 给特定用户返回他的举报记录（包含处理结果，举报内容，id等，只返回本人提交的记录）
# ==========================================
@router.get("/{report_id}", response_model=ResponseBase[ReportResponse])
async def get_report(report_id: int, current_user: User = Depends(get_current_user)):
    """
    这个函数是用来获取特定用户的举报记录的，只有登录用户会正确返回结果
    """
    report = await Report.get_or_none(id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="找不到该举报记录")
        
    if report.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看他人的举报记录")
        
        
    return success_response(report)

# ==========================================
# 管理员处理举报记录（包含处理结果，举报内容，id等，管理员才可以查看）
# ==========================================
@router.put("/{report_id}", response_model=ResponseBase[ReportResponse])
async def update_report_status(report_id: int, payload: ReportUpdate, current_user: User = Depends(get_current_user)):
    """
    这个函数是用来管理员处理举报记录的
    """
    # 使用鉴权依赖确保只有管理员及以上权限可以访问
    ensure_admin_or_super_root(current_user, required_permission="report.manage")
    
    report = await Report.get_or_none(id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="找不到该举报记录")
        
    report.status = payload.status.value
    await report.save(update_fields=["status"])
    
    return success_response(report)
