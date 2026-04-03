from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from peewee import JOIN
from pydantic import BaseModel

from server.database.connect import Database
from server.database.models import Letter, LetterLike, MoodType, PublicLetterFlow, User
from server.schema.letter import (
    LetterData,
    LettersData,
    LettersResponse,
    LikeData,
    LikeResponse,
    ShareData,
    ShareResponse,
)
from server.utils.auth import get_current_user
from server.utils.image import convert_to_webp

router = APIRouter()


class ShareRequest(BaseModel):
    content: Optional[str] = Form(None)
    image: Optional[UploadFile] = File(None)
    latitude: float = Form(...)
    longitude: float = Form(...)
    location: str = Form(...)
    is_public: int = Form(...)
    mood: Optional[str] = Form(None)


class FetchRequest(BaseModel):
    page: int = 1
    limit: int = 10
    keyword: Optional[str] = ""


class LikeRequest(BaseModel):
    letter_id: int


@router.post("/share", response_model=ShareResponse)
async def share(
    req: ShareRequest = Form(),
    user: Optional[User] = Depends(get_current_user),
) -> ShareResponse:
    """
    校园信笺上传接口。
    要求 content 和 image 至少有一个非空。
    """
    if not user:
        return ShareResponse(success=False, code=401, message="未授权或登录已过期")

    if not req.content and not req.image:
        return ShareResponse(
            success=False, code=400, message="文本内容和图片至少需要提供一个"
        )

    db = Database()
    with db.connection_context():
        try:
            # 1. 处理图片存储
            image_record = None
            if req.image:
                if not req.image.content_type or not req.image.content_type.startswith(
                    "image/"
                ):
                    return ShareResponse(
                        success=False, code=400, message="上传的文件必须是图片"
                    )
                image_record = convert_to_webp(req.image.file)

            # 2. 处理心情标签
            mood_record = None
            if req.mood:
                mood_record, _ = MoodType.get_or_create(name=req.mood)

            # 3. 创建信笺记录
            letter = Letter.create(
                user_id=user,
                content=req.content,
                image=image_record,
                mood_type=mood_record,
                latitude=req.latitude,
                longitude=req.longitude,
                location=req.location,
                is_public=bool(req.is_public),
            )

            return ShareResponse(
                success=True,
                message="发布成功",
                data=ShareData(
                    letter_id=letter.id,
                    created_at=letter.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        except Exception as e:
            return ShareResponse(success=False, code=500, message=f"发布失败: {e}")


@router.post("/fetch", response_model=LettersResponse)
async def fetch(
    req: FetchRequest,
    user: Optional[User] = Depends(get_current_user),
) -> LettersResponse:
    """
    分页获取公开信笺列表。
    """
    if req.keyword and len(req.keyword) > 20:
        return LettersResponse(
            success=False, code=400, message="搜索关键词长度不能超过20个字符"
        )
    if req.keyword and not user:
        return LettersResponse(success=False, code=401, message="搜索功能需要登录授权")

    db = Database()
    with db.connection_context():
        try:
            # 1. 基础查询拼接
            query = PublicLetterFlow.select(
                PublicLetterFlow, MoodType.name.alias("mood_name")
            ).join(
                MoodType, JOIN.LEFT_OUTER, on=(PublicLetterFlow.mood_id == MoodType.id)
            )

            # 2. 处理模糊搜索
            if req.keyword:
                query = query.where(
                    (PublicLetterFlow.content.contains(req.keyword))
                    | (PublicLetterFlow.location.contains(req.keyword))
                )

            # 3. 按时间倒序
            query = query.order_by(PublicLetterFlow.created_at.desc())

            # 采用 "Limit + 1" 法替代耗时的 count()
            fetch_limit = req.limit + 1
            offset = (req.page - 1) * req.limit

            # 使用 .dicts() 直接获取字典，极大提升 Python 层面的处理速度
            raw_data = list(query.offset(offset).limit(fetch_limit).dicts())

            # 判断是否有下一页
            has_more = len(raw_data) > req.limit

            # 截除多查询出来的那 1 条数据，只保留当前页需要的数据
            if has_more:
                raw_data = raw_data[: req.limit]

            # ====== 数据组装区 ======
            letter_list = []
            for item in raw_data:
                # 处理图片路径
                image_url = None
                if item.get("image_url"):
                    image_url = f"/image/{item['image_url']}.webp"

                # 处理头像路径
                avatar_url = "/image/avatar.webp"
                if item.get("avatar_url"):
                    avatar_url = f"/image/{item['avatar_url']}.webp"

                # 处理日期格式
                created_at_val = item.get("created_at")
                if hasattr(created_at_val, "strftime"):
                    created_at_str = created_at_val.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    created_at_str = str(created_at_val)

                letter_list.append(
                    LetterData(
                        letter_id=item["id"],
                        content=item.get("content"),
                        image=image_url,
                        latitude=item["latitude"],
                        longitude=item["longitude"],
                        location=item["location"],
                        likes_count=item.get("likes_count", 0),
                        mood=item.get("mood_name"),
                        username=item.get("username", "匿名用户"),
                        avatar=avatar_url,
                        created_at=created_at_str,
                    )
                )

            return LettersResponse(
                success=True,
                message="获取成功",
                data=LettersData(list=letter_list, has_more=has_more),
            )
        except Exception as e:
            return LettersResponse(
                success=False, code=500, message=f"获取失败: {str(e)}"
            )


@router.post("/like", response_model=LikeResponse)
async def like(
    req: LikeRequest,
    user: Optional[User] = Depends(get_current_user),
) -> LikeResponse:
    """
    信笺点赞接口。
    使用 LetterLike 表确保幂等性（每个用户对每封信只能点赞一次）。
    """
    if not user:
        return LikeResponse(success=False, code=401, message="未授权或登录已过期")

    db = Database()
    with db.connection_context():
        try:
            letter = Letter.get_or_none(Letter.id == req.letter_id)
            if not letter:
                return LikeResponse(success=False, code=404, message="信笺不存在")

            # 1. 检查是否已经点赞
            like_record, created = LetterLike.get_or_create(
                user_id=user.id, letter_id=letter.id
            )

            if not created:
                # 如果已经存在点赞记录，则不做任何修改，直接返回
                is_liked = True
                message = "已经点过赞了"
            else:
                # 如果是新点赞，增加点赞数
                letter.likes_count += 1
                letter.save()
                is_liked = True
                message = "点赞成功"

            return LikeResponse(
                success=True,
                message=message,
                data=LikeData(likes_count=letter.likes_count, is_liked=is_liked),
            )
        except Exception as e:
            return LikeResponse(success=False, code=500, message=f"操作失败: {str(e)}")
