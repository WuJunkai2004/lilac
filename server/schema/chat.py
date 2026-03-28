from datetime import datetime
from typing import List

from server.schema.base import DataSchema, ResponseSchema


class ChatMessageData(DataSchema):
    role: str
    content: str
    created_at: datetime


class ChatResponse(ResponseSchema[ChatMessageData]):
    pass


class ChatHistoryData(DataSchema):
    history: List[ChatMessageData]


class ChatHistoryResponse(ResponseSchema[ChatHistoryData]):
    pass


class ChatActionResponse(ResponseSchema[DataSchema]):
    pass
