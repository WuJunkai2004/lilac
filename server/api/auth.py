import hashlib
import re
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from server.database.connect import Database
from server.database.models import User
from server.schema.auth import AuthData, AuthResponse

router = APIRouter()


class AuthRequest(BaseModel):
    # 只能有字母、数字和下划线，且长度为5-15
    username: str = Field(..., pattern=r"^[a-zA-Z0-9_]{5,15}$")
    # 密码长度限制 8-31，具体正则由 validator 处理
    password: str = Field(..., min_length=8, max_length=31)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        # Pydantic pattern 不支持 lookahead，改用 re 模块
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,31}$", v):
            raise ValueError("密码必须至少包含一个字母和一个数字")
        return v


def get_password_hash(password: str) -> str:
    """简单的 SHA-256 密码哈希，生产环境建议使用 passlib[bcrypt]"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return get_password_hash(plain_password) == hashed_password


def generate_token() -> str:
    """生成 64 位随机会话 Token"""
    return secrets.token_hex(32)


def get_avator(user: User) -> str:
    """获取用户头像 URL，返回默认头像如果没有设置"""
    if user.avatar:
        return f"/image/{user.avatar.name}"
    return "/image/avatar"


@router.post("/register", response_model=AuthResponse)
def register(req: AuthRequest) -> AuthResponse:
    """用户注册接口"""
    # 直接在函数作用域内获取 db 实例
    db = Database()
    with db.connection_context():
        # 检查用户名是否存在
        if User.select().where(User.username == req.username).exists():
            return AuthResponse(success=False, code=400, message="用户名已存在")

        # 创建新用户
        token = generate_token()
        expires_at = datetime.now() + timedelta(days=7)  # Token 7 天过期

        try:
            user = User.create(
                username=req.username,
                password_hash=get_password_hash(req.password),
                session_token=token,
                token_expires_at=expires_at,
            )
            return AuthResponse(
                success=True,
                data=AuthData(
                    token=token,
                    username=user.username,
                    avatar_url=get_avator(user),
                ),
            )
        except Exception as e:
            return AuthResponse(success=False, code=500, message=f"注册失败: {str(e)}")


@router.post("/login", response_model=AuthResponse)
def login(req: AuthRequest) -> AuthResponse:
    """用户登录接口"""
    # 直接在函数作用域内获取 db 实例
    db = Database()
    with db.connection_context():
        # 查找用户
        user = User.get_or_none(User.username == req.username)

        if not user or not verify_password(req.password, user.password_hash):
            return AuthResponse(success=False, code=400, message="用户名或密码错误")

        # 更新 Session Token
        new_token = generate_token()
        user.session_token = new_token
        user.token_expires_at = datetime.now() + timedelta(days=7)
        user.save()

        return AuthResponse(
            success=True,
            data=AuthData(
                token=new_token,
                username=user.username,
                avatar_url=get_avator(user),
            ),
        )
