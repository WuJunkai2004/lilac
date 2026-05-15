import datetime

from peewee import JOIN, fn

from server.database.connect import Database
from server.database.models import ChatMessage, ChatSession
from server.tasks.register import register
from server.utils.logger import log


def delete_session(session: ChatSession):
    """
    删除指定的会话及其所有关联消息。
    """
    try:
        session_id = session.id
        # 删除该会话下的所有消息
        ChatMessage.delete().where(ChatMessage.session_id == session_id).execute()
        # 删除会话本身
        session.delete_instance()
        log("clear_chat_sessions").info(f"已删除会话 {session_id} 及其关联消息")
        return True
    except Exception as e:
        log("clear_chat_sessions").error(f"删除会话 {session.id} 失败: {e}")
        return False


@register("clear_chat_sessions")
def clear_chat_sessions():
    """
    清理过期的聊天会话。
    条件：最后一条消息在 1 小时前，或者没有消息且会话创建于 1 小时前
    """
    db = Database()
    with db.connection_context():
        now = datetime.datetime.now()
        # 今天凌晨 0 点
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # 1 小时前
        one_hour_ago = now - datetime.timedelta(hours=1)

        # 查找符合条件的会话 (与 summary.py 一致)
        query = (
            ChatSession.select()
            .join(ChatMessage, JOIN.LEFT_OUTER)
            .where(ChatSession.created_at < today_start)
            .where(ChatSession.session_type == "daily")
            .group_by(ChatSession.id)
            .having(
                (fn.MAX(ChatMessage.created_at) < one_hour_ago)
                | (
                    fn.MAX(ChatMessage.created_at).is_null()
                    & (ChatSession.created_at < one_hour_ago)
                )
            )
            .order_by(ChatSession.created_at.asc())
        )

        count = 0
        for session in query:
            if delete_session(session):
                count += 1

        if count > 0:
            log("clear_chat_sessions").info(
                f"清理任务执行完毕，共删除 {count} 个过期会话"
            )
