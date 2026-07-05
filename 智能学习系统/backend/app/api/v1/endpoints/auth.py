"""
用户认证接口 - 注册、登录、密码修改
"""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.core.security import (
    get_password_hash, verify_password, create_access_token, 
    decode_token, get_current_user_id
)
from app.models.database import User, UserRole, get_db

router = APIRouter()
security = HTTPBearer(auto_error=False)


# ========== 请求/响应模型 ==========

class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    email: Optional[str] = Field(None, description="邮箱（可选）")
    phone: Optional[str] = Field(None, description="手机号（可选）")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, max_length=100, description="新密码")


class PasswordResetRequest(BaseModel):
    """重置密码请求（通过邮箱/手机）"""
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")


class UserResponse(BaseModel):
    """用户信息响应"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    """Token 响应"""
    model_config = ConfigDict(from_attributes=True)
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


# ========== 接口实现 ==========

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册
    
    - 用户名唯一，3-50 位字母数字
    - 密码至少 6 位
    - 可选填邮箱和手机号
    """
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )
    
    # 检查邮箱是否已存在
    if request.email:
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
    
    # 检查手机号是否已存在
    if request.phone:
        existing_phone = db.query(User).filter(User.phone == request.phone).first()
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )
    
    # 密码强度检查
    if len(request.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码至少6位"
        )
    
    # 创建新用户
    try:
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            username=request.username,
            email=request.email,
            phone=request.phone,
            hashed_password=get_password_hash(request.password),
            nickname=request.nickname or request.username,
            role="student",  # 默认角色为学生
            status="active"
        )
        
        db.add(new_user)
        
        # 创建默认角色记录
        user_role = UserRole(
            user_id=user_id,
            role="student",
            permissions='["read", "write", "chat"]'
        )
        db.add(user_role)
        
        db.commit()
        db.refresh(new_user)
        
        # 生成 Token
        access_token = create_access_token(data={"sub": user_id})
        
        return make_token_response(access_token, new_user)
    except Exception as e:
        db.rollback()
        print(f"[ERROR] 注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录
    
    - 支持用户名 + 密码登录
    - 返回 JWT Token
    """
    # 查找用户
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 验证密码
    try:
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误"
            )
    except Exception as e:
        print(f"[ERROR] 密码验证异常: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查用户状态
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用，请联系管理员"
        )
    
    # 更新最后登录时间
    user.last_login_at = datetime.utcnow()
    db.commit()
    
    # 生成 Token
    access_token = create_access_token(data={"sub": user.id})
    
    return make_token_response(access_token, user)


@router.post("/logout")
async def logout():
    """
    用户退出登录
    
    - 前端删除 Token 即可
    - 后端记录日志（可选）
    """
    return {"message": "退出登录成功"}


@router.get("/me")
async def get_current_user_info(
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户信息
    
    - 需要 Bearer Token 认证
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user_to_dict(user)


# 辅助函数：将 SQLAlchemy User 对象转换为字典
def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "role": user.role,
        "created_at": user.created_at,
    }


@router.put("/password", response_model=dict)
async def change_password(
    request: PasswordChangeRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    修改密码
    
    - 需要提供旧密码验证
    - 新密码至少 6 位
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证旧密码
    if not verify_password(request.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="旧密码错误"
        )
    
    # 更新密码
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "密码修改成功，请重新登录"}


@router.post("/reset-password", response_model=dict)
async def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    重置密码（通过邮箱/手机）
    
    - 发送重置链接/验证码到邮箱或手机
    - 当前为模拟实现，实际需接入邮件/短信服务
    """
    if not request.email and not request.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请提供邮箱或手机号"
        )
    
    # 查找用户
    user = None
    if request.email:
        user = db.query(User).filter(User.email == request.email).first()
    elif request.phone:
        user = db.query(User).filter(User.phone == request.phone).first()
    
    if not user:
        # 为了安全，不暴露用户是否存在
        return {"message": "如果该邮箱/手机号已注册，重置链接将发送至您的邮箱/手机"}
    
    # TODO: 实际实现需要：
    # 1. 生成重置 Token
    # 2. 发送邮件/短信
    # 3. 用户点击链接后设置新密码
    
    return {
        "message": "如果该邮箱/手机号已注册，重置链接将发送至您的邮箱/手机",
        "note": "【模拟】实际生产环境需接入邮件/短信服务"
    }


@router.put("/profile")
async def update_profile(
    nickname: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    avatar: Optional[str] = None,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    更新用户资料
    
    - 支持修改昵称、邮箱、手机号、头像
    - 需要 Bearer Token 认证
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查邮箱唯一性
    if email and email != user.email:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        user.email = email
    
    # 检查手机号唯一性
    if phone and phone != user.phone:
        existing = db.query(User).filter(User.phone == phone).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被使用"
            )
        user.phone = phone
    
    if nickname:
        user.nickname = nickname
    if avatar:
        user.avatar = avatar
    
    db.commit()
    db.refresh(user)
    
    return user_to_dict(user)


# 用于直接返回字典的辅助函数
def make_token_response(access_token: str, user_obj) -> dict:
    """手动构造 Token 响应字典，避免 Pydantic V2 验证问题"""
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 60 * 24 * 7,
        "user": user_to_dict(user_obj)
    }
