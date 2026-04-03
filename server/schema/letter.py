from typing import List, Optional

from server.schema.base import DataSchema, ResponseSchema


class ShareData(DataSchema):
    letter_id: int
    created_at: str


class ShareResponse(ResponseSchema[ShareData]):
    pass


class LetterData(DataSchema):
    letter_id: int
    content: Optional[str] = None
    image: Optional[str] = None
    latitude: float
    longitude: float
    location: str
    likes_count: int
    mood: Optional[str] = None
    username: str
    avatar: str
    created_at: str


class LettersData(DataSchema):
    list: List[LetterData]
    has_more: bool


class LettersResponse(ResponseSchema[LettersData]):
    pass
