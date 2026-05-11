import re
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator

from server.database.connect import Database
from server.database.models import User
from server.schema.profile import ProfileResponse
from server.utils.auth import get_current_user, get_password_hash, verify_password

router = APIRouter()


class UpdateUsernameRequest(BaseModel):
    username: str = Field(..., pattern=r"^[a-zA-Z0-9_]{5,15}$")


class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=31)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,31}$", v):
            raise ValueError("密码必须至少包含一个字母和一个数字")
        return v


@router.post("/username", response_model=ProfileResponse)
def update_username(
    req: UpdateUsernameRequest, user: Optional[User] = Depends(get_current_user)
) -> ProfileResponse:
    """
    修改当前用户的用户名。
    """
    if not user:
        return ProfileResponse(success=False, code=401, message="未授权或登录已过期")

    db = Database()
    with db.connection_context():
        # 检查用户名是否已存在
        if (
            User.select()
            .where((User.username == req.username) & (User.id != user.id))
            .exists()
        ):
            return ProfileResponse(success=False, code=400, message="用户名已存在")

        user.username = req.username  # type: ignore
        user.save()

        return ProfileResponse(success=True, message="用户名修改成功")


@router.post("/password", response_model=ProfileResponse)
def update_password(
    req: UpdatePasswordRequest, user: Optional[User] = Depends(get_current_user)
) -> ProfileResponse:
    """
    修改当前用户的密码。
    """
    if not user:
        return ProfileResponse(success=False, code=401, message="未授权或登录已过期")

    db = Database()
    with db.connection_context():
        # 验证旧密码
        if not verify_password(req.old_password, str(user.password_hash)):
            return ProfileResponse(success=False, code=400, message="旧密码错误")

        # 更新密码
        user.password_hash = get_password_hash(req.new_password)  # type: ignore
        user.save()

        return ProfileResponse(success=True, message="密码修改成功")
