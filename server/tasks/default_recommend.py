import datetime
import random
import re

from server.database.connect import Database
from server.database.models import AIFeedback, MoodEntry, MoodType, User
from server.tasks.register import register
from server.utils.agent import chat_messages, create_conversation
from server.utils.logger import log


@register("default_recommend")
def default_recommend():
    now = datetime.datetime.now()

    # 凌晨2点之前执行，作为当日默认推荐补全
    if now.hour >= 2:
       return

    today = now.date()
    db = Database()
    with db.connection_context():
        # 获取默认用户
        try:
            default_user = User.get(User.username == "default")
        except Exception:
            log("default_recommend").error(
                "未找到 'default' 用户，请确保数据库已初始化"
            )
            return

        # 检查是否已经存在今天的默认推荐（挂载在 default 用户下）
        exists = (
            AIFeedback.select()
            .join(MoodEntry)
            .where((MoodEntry.user_id == default_user) & (MoodEntry.log_date == today))
            .exists()
        )

        if exists:
            return

        # 生成通用的推荐内容
        recommendation = generate_default_recommendation()
        if not recommendation:
            return

        # 获取默认心情类型（例如“宁静”）
        try:
            default_mood = MoodType.get(MoodType.name == "宁静")
        except Exception:
            log("default_recommend").error("数据库中缺失 '宁静' 心情类型")
            return

        try:
            # 为 default 用户创建今天的 MoodEntry 和 AIFeedback
            mood_entry, _ = MoodEntry.get_or_create(
                user_id=default_user,
                log_date=today,
                defaults={"mood_type_id": default_mood},
            )

            AIFeedback.create(
                mood_entry_id=mood_entry,
                review_content="祝你今天有好心情！",
                rec_activity=recommendation["activity"],
                rec_food=recommendation["food"],
            )
            log("default_recommend").info("已为 'default' 用户生成并存储今日默认推荐")
        except Exception as e:
            log("default_recommend").error(f"保存 'default' 用户默认推荐失败: {e}")


def generate_default_recommendation():
    """使用 AI 生成一份通用的今日推荐"""
    now = datetime.datetime.now()
    # 随机主题增加多样性
    themes = ["宁静", "活力", "喜悦", "放松", "探索", "温馨", "浪漫", "清新"]
    theme = random.choice(themes)

    prompt = f"""你是一个哈尔滨工业大学（深圳校区）的学生开发的 AI 助手，专门为学生提供每日活动和美食推荐。
你服务的对象是深圳校区的学生，他们喜欢在校园附近寻找有趣的活动和美味的食物。
今天是{now.strftime("%Y年%m月%d日")}。请以此日期为背景，并以“{theme}”为主题，为用户推荐一个今天的建议活动和一个今日美食。

建议活动格式为："在xxxx做xx"。只需要一个建议，句子长度不超过20字。
今日美食格式为："某处的某种食物"。这里的某处，不能是宽泛的地点（如"附近"、"食堂"），而应该是一个具体的的餐厅、档口等。只需要一个建议，句子长度不超过20字/

请严格按照以下格式输出：
建议活动：<活动内容>
今日美食：<美食内容>
"""

    try:
        # 创建一个临时会话
        conv_id = create_conversation("system_default")
        if not conv_id:
            return None

        response = chat_messages(conv_id, "system_default", prompt)
        data = response.json()
        reply = data.get("answer", "")

        def extract(keyword, text):
            pattern = rf"{keyword}：\s*(.*?)(?=\n\w+：|$)"
            match = re.search(pattern, text, re.S)
            if not match:
                return ""
            result = match.group(1).strip()
            # 去除可能包裹的尖括号
            if result.startswith("<"):
                result = result[1:]
            if result.endswith(">"):
                result = result[:-1]
            return result

        activity = extract("建议活动", reply)
        food = extract("今日美食", reply)

        if not activity or not food:
            log("default_recommend").warning(f"AI 回复格式解析失败。回复内容：{reply}")
            return None

        return {"activity": activity, "food": food}
    except Exception as e:
        log("default_recommend").error(f"调用 AI 生成默认推荐失败: {e}")
        return None
