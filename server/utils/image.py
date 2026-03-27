import uuid
from pathlib import Path

from PIL import Image as PILImage

from server.database.models import Image
from server.utils.file import folder


def register_image(file_name: str) -> Image:
    """注册图片到数据库，只传入文件名不传入具体路径和后缀"""
    return Image.create(name=file_name)


def convert_to_webp(file_handler) -> Image:
    """将图片转换为 webp 格式并保存到 folder.IMAGES，然后注册到数据库"""
    img = PILImage.open(file_handler)
    file_stem = str(uuid.uuid4())

    if not folder.IMAGES.exists():
        folder.IMAGES.mkdir(parents=True, exist_ok=True)

    save_path = folder.IMAGES / f"{file_stem}.webp"
    img.save(save_path, "WEBP")

    return register_image(file_stem)


def get_image_path(image_name: str) -> Path:
    """通过图片名称获取图片的具体路径"""
    # 兼容带后缀和不带后缀的情况
    if image_name.endswith(".webp"):
        return folder.IMAGES / image_name
    return folder.IMAGES / f"{image_name}.webp"


def save_image(file_path: Path) -> Image:
    """通过具体路径保存图片，统一转换为 webp 并注册"""
    with open(file_path, "rb") as f:
        return convert_to_webp(f)
