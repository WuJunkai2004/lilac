from typing import List

from pydantic import RootModel

from server.schema.base import DataSchema, ResponseSchema


class DayMoodData(DataSchema):
    date: str
    mood: str


class CalendarMoodData(DataSchema, RootModel[List[DayMoodData]]):
    pass


class CalendarResponse(ResponseSchema[CalendarMoodData]):
    pass


class DetailData(DataSchema):
    summary: str
    activity: str
    food: str


class DetailResponse(ResponseSchema[DetailData]):
    pass


class OverviewData(DataSchema):
    mood: str
    count: int


class OverviewListData(DataSchema, RootModel[List[OverviewData]]):
    pass


class OverviewResponse(ResponseSchema[OverviewListData]):
    pass
