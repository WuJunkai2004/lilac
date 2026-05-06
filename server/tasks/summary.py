import datetime
import re

from peewee import JOIN, fn

from server.database.connect import Database
from server.database.models import (
    AIFeedback,
    ChatMessage,
    ChatSession,
    MoodEntry,
    MoodType,
)
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
            .order_by(ChatSession.created_at.asc())
        )

        for session in query:
            mood_data = summary_mood(session)
            if not mood_data:
                continue
            success = insert_mood(session, mood_data)
            if not success:
                log("summary").error(f"为会话 {session.id} 插入情绪记录失败")
                continue

            ChatMessage.delete().where(ChatMessage.session_id == session.id).execute()
            session.delete_instance()
            log("summary").info(f"已删除会话 {session.id} 及其关联消息")


def insert_mood(session: ChatSession, mood_data: dict) -> bool:
    try:
        mood_name = mood_data.get("mood", "")
        review_content = mood_data.get("review", "")
        rec_activity = mood_data.get("activity", "")
        rec_food = mood_data.get("food", "")

        mood_type = MoodType.get(MoodType.name == mood_name)
        log_date_a = session.created_at.date()  # type: ignore
        log_date_next = log_date_a + datetime.timedelta(days=1)

        # 1. 处理 A 日的记录 (心情 + 总结)
        mood_entry_a, created_a = MoodEntry.get_or_create(
            user_id=session.user_id,
            log_date=log_date_a,
            defaults={"mood_type_id": mood_type},
        )
        if not created_a:
            mood_entry_a.mood_type_id = mood_type
            mood_entry_a.save()

        ai_feedback_a, created_f_a = AIFeedback.get_or_create(
            mood_entry_id=mood_entry_a,
            defaults={"review_content": review_content},
        )
        if not created_f_a:
            ai_feedback_a.review_content = review_content
            ai_feedback_a.save()

        # 2. 处理 A+1 日的记录 (推荐活动 + 美食)
        # 为 A+1 日创建或获取 MoodEntry，暂时沿用 A 日的心情类型作为建议基准
        mood_entry_next, _ = MoodEntry.get_or_create(
            user_id=session.user_id,
            log_date=log_date_next,
            defaults={"mood_type_id": mood_type},
        )

        ai_feedback_next, created_f_next = AIFeedback.get_or_create(
            mood_entry_id=mood_entry_next,
            defaults={
                "review_content": "今日总结还在生成中...",
                "rec_activity": rec_activity,
                "rec_food": rec_food,
            },
        )
        if not created_f_next:
            ai_feedback_next.rec_activity = rec_activity
            ai_feedback_next.rec_food = rec_food
            ai_feedback_next.save()

    except Exception:
        log("summary").error("插入情绪记录或 AI 反馈失败", exc_info=True)
        return False
    return True


prompt_summary_mood = """对会话进行总结，提取用户的情绪倾向，并给出心理总结和建议。

1. 从以下列表中选择一个最符合用户情绪倾向的标签：
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

2. 生成一段不超过80字的心理总结，用第二人称对用户说，内容应结合用户今日在会话中提到的内容。
例如："这一天你留下了深沉而宁静的回响。AI 观察到你在平衡学业与自我关怀方面做得很好。"

3. 推荐一个明天的建议活动，结合用户的心情，格式为："在xxxx做xx"。

4. 推荐一个今日美食，结合用户的心情，格式为："某处的某种食物"。

请严格按照以下格式输出：
用户情绪倾向：<标签>
心理总结：<总结内容>
建议活动：<活动内容>
今日美食：<美食内容>
"""


def summary_mood(session: ChatSession) -> dict:
    try:
        response = chat_messages(
            str(session.conversation_id),
            str(session.user_id.username),
            prompt_summary_mood,
        )
        data = response.json()
        reply = data.get("answer", "")

        # 从模型的回复中提取数据，使用更健壮的正则表达式
        def extract(keyword, text):
            pattern = rf"{keyword}：\s*(.*?)(?=\n\w+：|$)"
            match = re.search(pattern, text, re.S)
            if not match:
                log("summary").warning(f"未找到关键词 '{keyword}' 的匹配项")
                return ""
            result = match.group(1).strip()
            if result.startswith("<"):
                result = result[1:]
            if result.endswith(">"):
                result = result[:-1]
            return result

        mood = extract("用户情绪倾向", reply)
        review = extract("心理总结", reply)
        activity = extract("建议活动", reply)
        food = extract("今日美食", reply)

        if not mood:
            log("summary").info(f"未能从模型回复中提取情绪倾向标签，回复内容：{reply}")
            return {}

        result = {
            "mood": mood,
            "review": review,
            "activity": activity,
            "food": food,
        }
        log("summary").info(f"会话 {session.id} 的提取结果：{result}")
        return result
    except Exception:
        log("summary").error(f"总结会话 {session.id} 失败", exc_info=True)
        return {}


if __name__ == "__main__":
    summary()
