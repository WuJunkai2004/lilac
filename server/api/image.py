from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from server.utils.image import get_image_path

router = APIRouter()


@router.get("/{image_name}", tags=["Images"])
async def get_image(image_name: str):
    """
    获取图片资源。
    支持 /image/xxx 和 /image/xxx.webp
    """
    path = get_image_path(image_name)

    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(path, media_type="image/webp")
