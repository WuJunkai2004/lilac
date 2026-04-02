from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel

from server.database.connect import Database
from server.database.models import Letter, MoodType, User
from server.schema.letter import ShareData, ShareResponse
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


@router.post("/share", response_model=ShareResponse)
async def share_letter(
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
