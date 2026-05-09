from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from peewee import fn
from pydantic import BaseModel, field_validator

from server.database.models import AIFeedback, Letter, MoodEntry, MoodType
from server.schema.mood import (
    CalendarMoodData,
    CalendarResponse,
    DayMoodData,
    DetailData,
    DetailResponse,
    OverviewData,
    OverviewListData,
    OverviewResponse,
)
from server.utils.auth import get_current_user

router = APIRouter()


class CalendarRequest(BaseModel):
    month: str  # 查询月份，格式为 YYYY-MM

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: str):
        # 验证日期格式是否正确
        try:
            year, month = map(int, v.split("-"))
            if not (1 <= month <= 12):
                raise ValueError
        except (ValueError, AttributeError):
            raise ValueError("月份格式错误，应为 YYYY-MM")
        return v


class DataStrRequest(BaseModel):
    date: str  # 日期，格式为 YYYY-MM-DD

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        # 验证日期格式是否正确
        def is_leap(y: int) -> bool:
            return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)

        year, month, day = map(int, v.split("-"))
        day_in_month = [
            31,
            29 if is_leap(year) else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ]
        if not (1 <= month <= 12) or not (1 <= day <= day_in_month[month - 1]):
            raise ValueError("日期格式错误，应为 YYYY-MM-DD")
        return v


@router.get("/calendar")
def calendar(
    request: CalendarRequest = Query(), user=Depends(get_current_user)
) -> CalendarResponse:
    if not user:
        return CalendarResponse(success=False, code=401, message="未登录")

    # 查询当前用户在指定月份的所有情绪记录
    # 格式化月份为 YYYY-MM% 进行前缀匹配，适用于 log_date (DateField)
    entries = (
        MoodEntry.select()
        .where(
            (MoodEntry.user_id == user.id)
            & (MoodEntry.log_date.cast("text").startswith(request.month))
        )
        .order_by(MoodEntry.log_date.asc())
    )

    day_mood_list = [
        DayMoodData(
            date=entry.log_date.strftime("%Y-%m-%d"), mood=entry.mood_type_id.name
        )
        for entry in entries
    ]

    return CalendarResponse(
        success=True, code=200, message="success", data=CalendarMoodData(day_mood_list)
    )


@router.get("/detail")
def detail(
    request: DataStrRequest = Query(), user=Depends(get_current_user)
) -> DetailResponse:
    if not user:
        return DetailResponse(success=False, code=401, message="未登录")

    # 查询该用户在该日期的情绪记录
    mood_entry = MoodEntry.get_or_none(
        MoodEntry.user_id == user.id, MoodEntry.log_date == request.date
    )

    if not mood_entry:
        return DetailResponse(success=False, code=404, message="未找到该日期的记录")

    # 查询对应的 AI 反馈
    ai_feedback = AIFeedback.get_or_none(AIFeedback.mood_entry_id == mood_entry.id)

    if not ai_feedback:
        return DetailResponse(success=False, code=404, message="总结生成中或未找到总结")

    return DetailResponse(
        success=True,
        code=200,
        message="success",
        data=DetailData(
            summary=ai_feedback.review_content,
            activity=ai_feedback.rec_activity or "",
            food=ai_feedback.rec_food or "",
        ),
    )


@router.get("/overview")
def overview(request: DataStrRequest = Query()) -> OverviewResponse:
    # 获取目标日期和昨天
    target_date = datetime.strptime(request.date, "%Y-%m-%d").date()
    yesterday = target_date - timedelta(days=1)

    counts = Counter()

    # 1. 统计昨天和今天 AI 总结的心情数量（按心情类型分组）
    ai_entries = (
        MoodEntry.select(MoodType.name, fn.COUNT(MoodEntry.id).alias("cnt"))
        .join(MoodType, on=(MoodEntry.mood_type_id == MoodType.id))
        .join(AIFeedback, on=(AIFeedback.mood_entry_id == MoodEntry.id))
        .where(MoodEntry.log_date << [target_date, yesterday])
        .group_by(MoodType.name)
    )
    for entry in ai_entries:
        counts[entry.name] += entry.cnt

    # 2. 统计今天用户发布的信笺里面的心情数量（按心情类型分组）
    letter_entries = (
        Letter.select(MoodType.name, fn.COUNT(Letter.id).alias("cnt"))
        .join(MoodType, on=(Letter.mood_type == MoodType.id))
        .where(Letter.created_at.cast("text").startswith(request.date))
        .group_by(MoodType.name)
    )
    for entry in letter_entries:
        counts[entry.name] += entry.cnt

    # 构造返回数据
    data = [OverviewData(mood=mood, count=count) for mood, count in counts.items()]

    return OverviewResponse(
        success=True,
        code=200,
        message="success",
        data=OverviewListData(data),
    )
