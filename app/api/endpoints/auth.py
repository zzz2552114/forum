from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.enums import TrustLevel, UserRole
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.api.deps import get_current_user
from app.models.authentication import MailAuth
from app.schemas.authentication import StuAuthRequest, StuAuthVerify, StuAuthResponse
import re
from datetime import datetime, timedelta, UTC
import random
import string

router = APIRouter()


# ==========================================
# 用户注册接口
# 接收明文密码并哈希化后存入数据库
# ==========================================
@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate):
    user = await User.get_or_none(username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")

    user_email = await User.get_or_none(email=user_in.email)
    if user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = await User.create(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=UserRole.USER,
        trust_level=TrustLevel.BASIC,
    )
    return user


# ==========================================
# 用户登录接口 (获取 JWT Token)
# 使用 OAuth2 密码模式，验证密码后下发身份凭证 (Token)
# ==========================================
@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_or_none(username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


# ==========================================
# 学生认证功能 (发送验证码)
# ==========================================
mail_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.)*edu(\.cn)?$")

@router.post("/stu-auth/send", response_model=StuAuthResponse)
async def send_stu_auth(
    req: StuAuthRequest,
    current_user: User = Depends(get_current_user)
):
    """
    此函数用来申请验证码
    在开发阶段，返回给前端的包中有发送到的邮箱和验证码，注意，没有接入发送服务，所以并不会实际发送
    """
    if current_user.trust_level >= TrustLevel.VERIFIED:
        return {"success": False, "message": "您已经是认证用户"}

    if not mail_pattern.match(req.email):
        return {"success": False, "message": "请输入有效的教育邮箱 (.edu 或 .edu.cn)"}

    # 冷却时间限制
    now = datetime.now(UTC).replace(tzinfo=None)
    
    last_record = await MailAuth.filter(
        user=current_user, 
        is_used=False
    ).order_by("-created_at").first()
    
    if last_record:
        # 冷却时间检查 (例如 60 秒内不允许重复发送)
        if now < last_record.created_at + timedelta(seconds=60):
            return {"success": False, "message": "发送太频繁，请等待 60 秒后再试"}
        
        # 超过 60 秒，但未使用的旧记录，直接删除，保证数据库只保留最新一条
        await last_record.delete()

    # 生成 6 位随机数字验证码
    code = "".join(random.choices(string.digits, k=6))
    
    # 存入数据库
    await MailAuth.create(
        code=code,
        user=current_user,
        email=req.email,
        school_name=req.school_name,
        expired_at= now + timedelta(minutes=5)
    )
    
    # 在没有真正接入邮件服务前，可以在终端打印出来看
    print(f"【模拟发送邮件】目标邮箱: {req.email}, 验证码: {code}")
    
    return {"success": True, "message": "验证码已发送到您的邮箱，请在 5 分钟内完成验证","sent_to":req.email,"code":code}

# ==========================================
# 学生认证功能 (校验验证码)
# ==========================================
@router.post("/stu-auth/verify", response_model=StuAuthResponse)
async def verify_stu_auth(
    req: StuAuthVerify,
    current_user: User = Depends(get_current_user)
):
    """
    此函数用来校验验证码,用户输入的验证码应该发送到这个url做校验
    """
    now = datetime.now(UTC).replace(tzinfo=None)
    
    # 查找该用户最新的一条未使用验证码
    auth_record = await MailAuth.filter(
        user=current_user,
        is_used=False
    ).order_by("-created_at").first()
    
    if not auth_record:
        return {"success": False, "message": "未找到验证记录，请先发送验证码"}
        
    # 如果超时或者错误次数达到 5 次
    if now > auth_record.expired_at or auth_record.attempts >= 5:
        await auth_record.delete()
        return {"success": False, "message": "验证码已过期或尝试次数过多，请重试"}
        
    # 增加尝试次数
    auth_record.attempts += 1
    await auth_record.save(update_fields=["attempts"])
    
    if req.code != auth_record.code:
        if auth_record.attempts >= 5:
            await auth_record.delete()
            return {"success": False, "message": "错误次数过多，验证码已失效，请重新发送"}
        return {"success": False, "message": f"验证码错误，您还有 {5 - auth_record.attempts} 次机会"}
        
    # 验证成功
    auth_record.is_used = True
    await auth_record.save(update_fields=["is_used"])
    
    # 自动升级用户
    current_user.trust_level = TrustLevel.VERIFIED
    current_user.school_name = auth_record.school_name
    await current_user.save(update_fields=["trust_level", "school_name"])
    
    return {"success": True, "message": "学生认证成功！"}
