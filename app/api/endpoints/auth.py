from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate):
    # Check if user exists
    user = await User.get_or_none(username=user_in.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    user_email = await User.get_or_none(email=user_in.email)
    if user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    # Create user
    user = await User.create(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    return user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_or_none(username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}
