from typing import Generic, Optional, TypeVar

from pydantic import BaseModel


class DataSchema(BaseModel):
    pass


T = TypeVar("T", bound="DataSchema")


class ResponseSchema(BaseModel, Generic[T]):
    success: bool
    code: int = 200
    message: str = ""
    data: Optional[T] = None
