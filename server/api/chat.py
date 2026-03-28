from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel

from server.database.connect import Database
from server.database.models import ChatMessage, ChatSession, User
from server.schema.chat import (
    ChatActionResponse,
    ChatHistoryData,
    ChatHistoryResponse,
    ChatMessageData,
    ChatResponse,
)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_type: str  # 'daily' or 'long-term'


# --- Dependencies ---


def get_current_user(
    token: Optional[str] = Header(None, alias="Authorization"),
) -> Optional[User]:
    """
    Dependency to get the current user from the token in the Authorization header.
    Expects 'Authorization: <token>' or 'Authorization: Bearer <token>'
    """
    if not token:
        return None

    if token.startswith("Bearer "):
        token = token[7:]

    db = Database()
    with db.connection_context():
        user = User.get_or_none(
            (User.session_token == token) & (User.token_expires_at > datetime.now())
        )
        return user


@router.post("/chat", response_model=ChatResponse)
def chat(
    req: ChatRequest, user: Optional[User] = Depends(get_current_user)
) -> ChatResponse:
    """
    用户发送消息，并获得 AI 回复。
    如果是该 session_type 的第一次聊天，将创建新会话。
    """
    if not user:
        return ChatResponse(success=False, code=401, message="未授权或登录已过期")

    if req.session_type not in ["daily", "long-term"]:
        return ChatResponse(success=False, code=400, message="非法的会话类型")

    db = Database()
    with db.connection_context():
        # 1. 获取或创建会话
        session, _ = ChatSession.get_or_create(user=user, session_type=req.session_type)

        # 2. 保存用户消息
        ChatMessage.create(session=session, role="user", content=req.message)

        # 3. 生成 AI 回复 (当前为占位回复，后续可接入 AI 模型)
        # TODO: 接入 AI 模型生成回复
        ai_reply_content = f"你好，我是 Lilac AI 助手。你刚才说：'{req.message}'。这是针对 {req.session_type} 会话的回复。"

        # 4. 保存 AI 回复
        ai_message = ChatMessage.create(
            session=session, role="assistant", content=ai_reply_content
        )

        return ChatResponse(
            success=True,
            data=ChatMessageData(
                role=ai_message.role,
                content=ai_message.content,
                created_at=ai_message.created_at,
            ),
        )


@router.get("/history", response_model=ChatHistoryResponse)
def history(
    session_type: str, user: Optional[User] = Depends(get_current_user)
) -> ChatHistoryResponse:
    """
    获取指定类型的聊天历史。
    """
    if not user:
        return ChatHistoryResponse(
            success=False, code=401, message="未授权或登录已过期"
        )

    if session_type not in ["daily", "long-term"]:
        return ChatHistoryResponse(success=False, code=400, message="非法的会话类型")

    db = Database()
    with db.connection_context():
        session = ChatSession.get_or_none(user=user, session_type=session_type)
        if not session:
            return ChatHistoryResponse(success=True, data=ChatHistoryData(history=[]))

        messages = (
            ChatMessage.select()
            .where(ChatMessage.session == session)
            .order_by(ChatMessage.created_at.asc())
        )

        history_list = [
            ChatMessageData(role=m.role, content=m.content, created_at=m.created_at)
            for m in messages
        ]

        return ChatHistoryResponse(
            success=True, data=ChatHistoryData(history=history_list)
        )


@router.delete("/delete", response_model=ChatActionResponse)
def delete(
    session_type: str, user: Optional[User] = Depends(get_current_user)
) -> ChatActionResponse:
    """
    删除指定类型的聊天历史。
    """
    if not user:
        return ChatActionResponse(success=False, code=401, message="未授权或登录已过期")

    if session_type not in ["daily", "long-term"]:
        return ChatActionResponse(success=False, code=400, message="非法的会话类型")

    db = Database()
    with db.connection_context():
        session = ChatSession.get_or_none(user=user, session_type=session_type)
        if not session:
            return ChatActionResponse(success=True, message="无历史记录可删除")

        # 删除该会话下的所有消息
        query = ChatMessage.delete().where(ChatMessage.session == session)
        query.execute()

        # 删除会话本身
        session.delete_instance()

        return ChatActionResponse(success=True, message="历史记录已成功删除")
