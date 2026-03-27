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
from server.utils.logger import log


def setup():
    """初始化数据库：创建表和视图"""
    # 获取数据库实例
    db = Database()
    # 连接数据库
    db.connect()

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
    # 注意：Peewee 默认外键字段名为 [field]_id
    db.execute_sql("""
    CREATE VIEW IF NOT EXISTS v_public_letter_flow AS
    SELECT
        l.id, l.content, i.file_path AS image_url, l.latitude, l.longitude,
        l.location_name, l.likes_count, l.view_count, l.created_at,
        u.username, ai.file_path AS avatar_url
    FROM letters l
    JOIN users u ON l.user_id = u.id
    LEFT JOIN images i ON l.image_id = i.id
    LEFT JOIN images ai ON u.avatar_id = ai.id
    WHERE l.is_public = 1
    ORDER BY l.created_at DESC;
    """)

    log("database").info("initialized database and created tables/views")
