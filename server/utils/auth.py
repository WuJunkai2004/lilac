from datetime import datetime
from typing import Optional

from fastapi import Header

from server.database.connect import Database
from server.database.models import User


def get_current_user(
    token: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[User]:
    """
    Dependency to get the current user from the token in the Authorization header.
    Expects 'Authorization: <token>' or 'Authorization: Bearer <token>'
    """
    if not token:
        return None

    if token.startswith("Bearer "):
        token = token[7:]

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
