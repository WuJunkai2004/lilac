from typing import Optional

from server.schema.base import DataSchema, ResponseSchema


class UserProfileData(DataSchema):
    username: str
    avatar_url: Optional[str] = None
    letter_count: int
    total_likes: int
    mood_day_count: int


class UserProfileResponse(ResponseSchema[UserProfileData]):
    pass
