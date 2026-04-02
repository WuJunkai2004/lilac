from typing import List

from pydantic import RootModel

from server.schema.base import DataSchema, ResponseSchema


class ShareData(DataSchema):
    letter_id: int
    created_at: str


class ShareResponse(ResponseSchema[ShareData]):
    pass


class LetterData(DataSchema):
    content: str
    image_url: str
    latitude: float
    longitude: float
    mood: str
    created_at: str


class LettersData(DataSchema, RootModel[List[LetterData]]):
    pass


class LettersResponse(ResponseSchema[LettersData]):
    pass
