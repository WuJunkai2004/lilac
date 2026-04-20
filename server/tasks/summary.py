import datetime
import re

from peewee import JOIN, fn

from server.database.connect import Database
from server.database.models import ChatMessage, ChatSession, MoodEntry, MoodType
from server.tasks.register import register
from server.utils.agent import chat_messages
from server.utils.logger import log


@register("summary")
def summary():
    db = Database()
    with db.connection_context():
        now = datetime.datetime.now()
        # 今天凌晨 0 点
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # 1 小时前
        one_hour_ago = now - datetime.timedelta(hours=1)

        # 查找符合条件的会话：
        # 1. 创建日期在今天之前 (today_start 之前)
        # 2. 最后一条消息的时间在 1 小时之前，或者没有消息且会话创建于 1 小时前
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
        )

        for session in query:
            mood = summary_mood(session)
            if not mood:
                continue
            success = insert_mood(session, mood)
            if not success:
                log("summary").error(f"为会话 {session.id} 插入情绪记录失败")
                continue

            ChatMessage.delete().where(ChatMessage.session_id == session.id).execute()
            session.delete_instance()
            log("summary").info(f"已删除会话 {session.id} 及其关联消息")


def insert_mood(session: ChatSession, mood_name: str) -> bool:
    try:
        mood_type = MoodType.get(MoodType.name == mood_name)
        log_date = session.created_at.date()  # type: ignore

        # 检查是否已存在该用户该日期的情绪记录
        # 如果存在，则更新；如果不存在，则创建
        mood_entry, created = MoodEntry.get_or_create(
            user_id=session.user_id,
            log_date=log_date,
            defaults={"mood_type_id": mood_type},
        )
        if not created:
            mood_entry.mood_type_id = mood_type
            mood_entry.save()

    except Exception:
        return False
    return True


prompt_summary_mood = """对会话进行总结，提取用户的情绪倾向
从以下列表中选择一个最符合用户情绪倾向的标签：
- 喜悦
- 孤独
- 宁静
- 忧郁
- 愤怒
- 放松
- 活力
- 浪漫
- 焦虑
- 神秘
你必须根据用户在会话中的消息内容，选择一个最符合用户情绪倾向的标签，并且只能选择一个标签。
用以下格式输出：
用户情绪倾向：<标签>
"""


def summary_mood(session: ChatSession) -> str:
    try:
        response = chat_messages(
            str(session.conversation_id),
            str(session.user_id.username),
            prompt_summary_mood,
        )
        data = response.json()
        reply = data.get("answer", "")

        # 从模型的回复中提取用户情绪倾向标签
        match = re.search(r"用户情绪倾向：(\w+)", reply)
        if not match:
            log("summary").info(f"未能从模型回复中提取情绪倾向标签，回复内容：{reply}")
            return ""
        mood = match.group(1)
        log("summary").info(f"会话 {session.id} 的用户情绪倾向标签：{mood}")
        return mood
    except Exception:
        log("summary").error(f"总结会话 {session.id} 的用户情绪倾向失败", exc_info=True)
        return ""


if __name__ == "__main__":
    summary()
