"""
安全工具 - JWT Token、密码哈希
"""
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import base64
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings


# HTTP Bearer 认证
security = HTTPBearer(auto_error=False)


def _prepare_password(password: str) -> str:
    """
    预处理密码：bcrypt 最大支持 72 字节
    使用 SHA256 哈希将任意长度密码转换为固定长度，再 base64 编码
    """
    # 使用 SHA256 生成固定长度的摘要
    sha256_hash = hashlib.sha256(password.encode('utf-8')).digest()
    # 转为 base64 字符串（约 44 字符，小于 72 字节）
    return base64.b64encode(sha256_hash).decode('ascii')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    import bcrypt
    prepared = _prepare_password(plain_password)
    # bcrypt 接受 bytes，将 prepared 编码为 ascii bytes
    prepared_bytes = prepared.encode("ascii")
    hashed_bytes = hashed_password.encode("ascii")
    return bcrypt.checkpw(prepared_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    import bcrypt
    prepared = _prepare_password(password)
    prepared_bytes = prepared.encode("ascii")
    # bcrypt.gensalt() 默认 rounds=12
    hashed = bcrypt.hashpw(prepared_bytes, bcrypt.gensalt())
    return hashed.decode("ascii")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """解码 JWT Token"""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """获取当前登录用户 ID（FastAPI Dependency）"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌中无用户信息",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


async def get_current_active_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """获取当前活跃用户 ID（检查用户状态）"""
    user_id = await get_current_user_id(credentials)
    
    # TODO: 可以在这里查询数据库检查用户是否被禁用
    # from app.models.database import User, SessionLocal
    # db = SessionLocal()
    # user = db.query(User).filter(User.id == user_id).first()
    # if not user or user.status != "active":
    #     raise HTTPException(status_code=403, detail="用户已被禁用")
    
    return user_id
