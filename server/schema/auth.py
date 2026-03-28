from typing import Optional

from server.schema.base import DataSchema, ResponseSchema


class AuthData(DataSchema):
    token: Optional[str] = None
    avatar_url: Optional[str] = None
    username: Optional[str] = None


class AuthResponse(ResponseSchema[AuthData]):
    pass
