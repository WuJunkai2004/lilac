from server.database.connect import Database
from server.database.models import Image, Letter, User
from server.task.register import register
from server.utils.image import get_image_path
from server.utils.logger import log


@register("clear_orphaned_images")
def clear_orphaned_images():
    """清理没有被任何表引用的图片及其文件"""
    db = Database()
    # 必须使用 connection_context，防止在多线程中造成连接泄漏
    with db.connection_context():
        try:
            # 获取被引用的图片外键集合
            user_avatars = User.select(User.avatar).where(User.avatar.is_null(False))
            letter_images = Letter.select(Letter.image).where(
                Letter.image.is_null(False)
            )

            # 使用子查询查找孤立的图片
            orphaned_images = Image.select().where(
                Image.img_id.not_in(user_avatars) & Image.img_id.not_in(letter_images)
            )

            deleted_count = 0
            for img in orphaned_images:
                # 1. 尝试删除本地物理文件
                file_path = get_image_path(img.name)
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except Exception as e:
                        log("clear").error(f"failed to delete file {file_path}: {e}")

                # 2. 删除数据库中的记录
                img.delete_instance()
                deleted_count += 1

            log("clear").info(f"cleared {deleted_count} orphaned images.")

        except Exception as e:
            log("clear").error(f"error during image clearance: {e}")
