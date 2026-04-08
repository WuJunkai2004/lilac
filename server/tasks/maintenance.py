import datetime

from server.database.connect import Database
from server.database.models import User
from server.tasks.register import register
from server.utils.logger import log


@register("clear_expired_sessions")
def clear_expired_sessions():
    """清理 User 表中已过期的 session_token"""
    db = Database()
    with db.connection_context():
        try:
            now = datetime.datetime.now()
            # 将过期的 session_token 和过期时间置为空
            # 这样可以强制这些用户重新登录
            affected_rows = (
                User.update(session_token=None, token_expires_at=None)
                .where(User.token_expires_at < now)
                .execute()
            )

            log("maintenance").info(f"cleared {affected_rows} expired sessions.")
        except Exception as e:
            log("maintenance").error(f"error during session clearance: {e}")


@register("database_maintenance")
def database_maintenance():
    """执行数据库 VACUUM 维护"""
    db = Database()
    # 必须开启连接。由于是同步函数由 asyncio.to_thread 执行，
    # 我们可以直接操作 db 对象
    try:
        # 使用 execute_sql 执行原始 SQL
        # VACUUM 在 SQLite 中不能在事务内运行，但 peewee 的 execute_sql 默认会尝试开启事务
        # 这里需要注意 SQLite 驱动的特性
        with db.connection_context():
            # 获取底层连接对象并确保不在事务中
            conn = db.connection()
            # 修改连接的隔离级别以允许运行 VACUUM (Peewee 默认会管理事务)
            old_isolation_level = conn.isolation_level
            conn.isolation_level = None  # Autocommit mode
            try:
                conn.execute("VACUUM")
                log("maintenance").info("database VACUUM completed.")
            finally:
                conn.isolation_level = old_isolation_level

    except Exception as e:
        log("maintenance").error(f"error during database maintenance: {e}")
