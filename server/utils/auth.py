import hashlib
from datetime import datetime
from typing import Optional

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from server.database.connect import Database
from server.database.models import User

security = HTTPBearer(auto_error=False)


def get_password_hash(password: str) -> str:
    """简单的 SHA-256 密码哈希，生产环境建议使用 passlib[bcrypt]"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return get_password_hash(plain_password) == hashed_password


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[User]:
    """
    Dependency to get the current user from the token in the Authorization header.
    Expects 'Authorization: Bearer <token>'
    """
    if not auth:
        return None

    token = auth.credentials

    db = Database()
    with db.connection_context():
        user = User.get_or_none(
            (User.session_token == token) & (User.token_expires_at > datetime.now())
        )
        return user


def get_avatar_url(user: User) -> str:
    """获取用户头像 URL，返回默认头像如果没有设置"""
    if user.avatar:
        return f"/image/{user.avatar.name}"
    return "/image/avatar"
