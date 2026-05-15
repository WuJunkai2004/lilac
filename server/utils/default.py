from datetime import datetime
from typing import Optional

from server.database.models import AIFeedback, MoodEntry, User
from server.utils.cache import cache
from server.utils.logger import log


@cache.enable(expire=6 * 3600, only_today=True)
def get_default_recommendation(date_str: str) -> Optional[tuple[str, str]]:
    """
    获取指定日期的默认推荐（活动, 美食）。
    使用缓存，有效期 6 小时，仅限当天。
    """
    # init 需要传入一个可变对象（如字典），缓存机制会在函数结束时保存它
    res, cached = cache.init({"activity": "", "food": "", "found": False})
    if cached:
        log("cache").info(f"Default recommendation cache hit for date {date_str}")
        if res["found"]:
            return (res["activity"], res["food"])
        return None

    try:
        # 转换日期字符串为 date 对象
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # 查询 default 用户的推荐信息
        feedback = (
            AIFeedback.select(AIFeedback.rec_activity, AIFeedback.rec_food)
            .join(MoodEntry)
            .join(User)
            .where((User.username == "default") & (MoodEntry.log_date == target_date))
            .first()
        )

        if feedback:
            res["activity"] = feedback.rec_activity or ""
            res["food"] = feedback.rec_food or ""
            res["found"] = True
            return (res["activity"], res["food"])

    except Exception as e:
        log("default").error(
            f"Failed to fetch default recommendation for {date_str}: {e}"
        )

    return None
