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



