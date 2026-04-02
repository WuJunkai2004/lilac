from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

from server.database.connect import Database
from server.database.models import User, UserProfile
from server.schema.user import UserProfileData, UserProfileResponse
from server.utils.auth import get_avatar_url, get_current_user
from server.utils.image import convert_to_webp

router = APIRouter()


class AvatarRequest(BaseModel):
    file: UploadFile = File(...)


@router.get("/profile", response_model=UserProfileResponse)
def get_profile(
    user: Optional[User] = Depends(get_current_user),
) -> UserProfileResponse:
    """
    获取当前用户的个人资料，包括用户名、头像、信笺数、总点赞数和心情记录天数。
    """
    if not user:
        return UserProfileResponse(
            success=False, code=401, message="未授权或登录已过期"
        )

    db = Database()
    with db.connection_context():
        # 从视图中获取统计信息
        profile = UserProfile.get_or_none(UserProfile.user_id == user.id)

        if not profile:
            # 如果视图中没有记录（通常不应该发生，因为视图是基于 users 表的），
            # 则手动构建一个基础资料
            return UserProfileResponse(
                success=True,
                data=UserProfileData(
                    username=str(user.username),
                    avatar_url=get_avatar_url(user),
                    letter_count=0,
                    total_likes=0,
                    mood_day_count=0,
                ),
            )

        return UserProfileResponse(
            success=True,
            data=UserProfileData(
                username=profile.username,
                avatar_url=get_avatar_url(user),
                letter_count=profile.letter_count,
                total_likes=int(
                    profile.total_likes
                ),  # TOTAL() in SQLite might return float
                mood_day_count=profile.mood_day_count,
            ),
        )


@router.post("/avatar", response_model=UserProfileResponse)
async def update_avatar(
    req: AvatarRequest = Depends(), user: Optional[User] = Depends(get_current_user)
) -> UserProfileResponse:
    """
    更新当前用户的头像。
    """
    if not user or not req.file.content_type:
        return UserProfileResponse(
            success=False, code=401, message="未授权或登录已过期"
        )

    # 验证文件类型
    if not req.file.content_type.startswith("image/"):
        return UserProfileResponse(
            success=False, code=400, message="上传的文件必须是图片"
        )

    db = Database()
    with db.connection_context():
        try:
            # 1. 将上传的图片转换为 webp 并保存，同时在数据库注册
            image_record = convert_to_webp(req.file.file)

            # 2. 更新用户的头像 ID
            user.avatar = image_record  # type: ignore
            user.save()

            # 3. 返回更新后的资料
            # 重新获取 profile 视图数据以确保数据一致性
            profile = UserProfile.get_or_none(UserProfile.user_id == user.id)

            if not profile:
                return UserProfileResponse(
                    success=True,
                    data=UserProfileData(
                        username=str(user.username),
                        avatar_url=get_avatar_url(user),
                        letter_count=0,
                        total_likes=0,
                        mood_day_count=0,
                    ),
                )

            return UserProfileResponse(
                success=True,
                data=UserProfileData(
                    username=profile.username,
                    avatar_url=get_avatar_url(user),
                    letter_count=profile.letter_count,
                    total_likes=int(profile.total_likes),
                    mood_day_count=profile.mood_day_count,
                ),
            )
        except Exception as e:
            return UserProfileResponse(
                success=False, code=500, message=f"更新头像失败: {str(e)}"
            )
