from server.database.connect import Database
from server.database.models import (
    AIFeedback,
    ChatMessage,
    ChatSession,
    Image,
    Letter,
    MoodEntry,
    MoodType,
    User,
)
from server.utils.file import copy, folder
from server.utils.image import register_image
from server.utils.logger import log


def init():
    """初始化数据库：初始化数据"""
    # 初始化默认数据，创建文件夹
    root = folder.ROOT
    datas = root / "datas"
    datas.mkdir(exist_ok=True)
    image = datas / "images"
    image.mkdir(exist_ok=True)

    # 初始化数据库内容
    db = Database()
    db.connect(True)
    # 初始化默认心情类型
    pass
    # 初始化默认用户数据
    if not User.select().where(User.username == "default").exists():
        # 先设置默认头像
        public_avatar = folder.PUBLIC / "avatar.webp"
        default_avatar = folder.IMAGES / "avatar.webp"
        try:
            copy(public_avatar, default_avatar, force=True)
        except Exception as e:
            log("database").error("failed to copy default avatar: %s", e)
        # 只传入文件名，不传路径和后缀，register_image 会自动处理
        avatar_image = register_image("avatar")

        default_user = User.create(
            username="default",
            password_hash="",
            avatar=avatar_image,
            session_token=None,
            token_expires_at=None,
        )
        log("database").info("created default user with id %d", default_user.id)


def setup():
    """初始化数据库：创建表和视图"""
    # 获取数据库实例
    db = Database()
    # 连接数据库
    db.connect(True)

    # 创建所有表
    models = [
        AIFeedback,
        ChatMessage,
        ChatSession,
        Image,
        Letter,
        MoodEntry,
        MoodType,
        User,
    ]
    db.create_tables(models)

    # 创建全校实时心情聚合视图 (v_school_mood_summary)
    db.execute_sql("""
    CREATE VIEW IF NOT EXISTS v_school_mood_summary AS
    SELECT
        mt.name AS mood_name,
        mt.color_code,
        mt.element_type,
        COUNT(me.id) AS count,
        DATE(me.log_date) AS summary_date
    FROM mood_entries me
    JOIN mood_types mt ON me.mood_type_id = mt.id
    GROUP BY mt.id, summary_date;
    """)

    # 创建公开信笺流视图 (v_public_letter_flow)
    # 注意：Peewee 默认外键字段名为 [field]_id，除非指定 column_name
    db.execute_sql("""
    CREATE VIEW IF NOT EXISTS v_public_letter_flow AS
    SELECT
        l.id, l.content, l.image, l.latitude, l.longitude, l.mood_type AS mood_id,
        l.location, l.likes_count, l.view_count, l.created_at,
        u.username, u.avatar
    FROM letters l
    JOIN users u ON l.user_id = u.id
    WHERE l.is_public = 1
    ORDER BY l.created_at DESC;
    """)

    # 创建个人资料概览视图 (v_user_profile)
    db.execute_sql("""
    CREATE VIEW IF NOT EXISTS v_user_profile AS
    SELECT
        u.id AS user_id,
        u.username,
        u.avatar,
        (SELECT COUNT(*) FROM letters l WHERE l.user_id = u.id) AS letter_count,
        (SELECT TOTAL(likes_count) FROM letters l WHERE l.user_id = u.id) AS total_likes,
        (SELECT COUNT(*) FROM mood_entries me WHERE me.user_id = u.id) AS mood_day_count
    FROM users u;
    """)

    log("database").info("initialized database and created tables/views")

    init()
