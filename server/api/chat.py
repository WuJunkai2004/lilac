from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from server.database.connect import Database
from server.database.models import ChatMessage, ChatSession, User

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_type: str  # 'daily' or 'long-term'


class ChatMessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    success: bool
    history: List[ChatMessageResponse]


class ChatActionResponse(BaseModel):
    success: bool
    message: str


# --- Dependencies ---


def get_current_user(
    token: Optional[str] = Header(None, alias="Authorization"),
) -> User:
    """
    Dependency to get the current user from the token in the Authorization header.
    Expects 'Authorization: <token>' or 'Authorization: Bearer <token>'
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    if token.startswith("Bearer "):
        token = token[7:]

    db = Database()
    with db.connection_context():
        user = User.get_or_none(
            (User.session_token == token) & (User.token_expires_at > datetime.now())
        )
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return user


@router.post("/chat", response_model=ChatMessageResponse)
def chat(
    req: ChatRequest, user: User = Depends(get_current_user)
) -> ChatMessageResponse:
    """
    用户发送消息，并获得 AI 回复。
    如果是该 session_type 的第一次聊天，将创建新会话。
    """
    if req.session_type not in ["daily", "long-term"]:
        raise HTTPException(status_code=400, detail="Invalid session type")

    db = Database()
    with db.connection_context():
        # 1. 获取或创建会话
        session, created = ChatSession.get_or_create(
            user=user, session_type=req.session_type
        )

        # 2. 保存用户消息
        ChatMessage.create(session=session, role="user", content=req.message)

        # 3. 生成 AI 回复 (当前为占位回复，后续可接入 AI 模型)
        # TODO: 接入 AI 模型生成回复
        ai_reply_content = f"你好，我是 Lilac AI 助手。你刚才说：'{req.message}'。这是针对 {req.session_type} 会话的回复。"

        # 4. 保存 AI 回复
        ai_message = ChatMessage.create(
            session=session, role="assistant", content=ai_reply_content
        )

        return ChatMessageResponse(
            role=ai_message.role,
            content=ai_message.content,
            created_at=ai_message.created_at,
        )


@router.get("/history", response_model=ChatHistoryResponse)
def history(
    session_type: str, user: User = Depends(get_current_user)
) -> ChatHistoryResponse:
    """
    获取指定类型的聊天历史。
    """
    if session_type not in ["daily", "long-term"]:
        raise HTTPException(status_code=400, detail="Invalid session type")

    db = Database()
    with db.connection_context():
        session = ChatSession.get_or_none(user=user, session_type=session_type)
        if not session:
            return ChatHistoryResponse(success=True, history=[])

        messages = (
            ChatMessage.select()
            .where(ChatMessage.session == session)
            .order_by(ChatMessage.created_at.asc())
        )

        history = [
            ChatMessageResponse(role=m.role, content=m.content, created_at=m.created_at)
            for m in messages
        ]

        return ChatHistoryResponse(success=True, history=history)


@router.delete("/delete", response_model=ChatActionResponse)
def delete(
    session_type: str, user: User = Depends(get_current_user)
) -> ChatActionResponse:
    """
    删除指定类型的聊天历史。
    """
    if session_type not in ["daily", "long-term"]:
        raise HTTPException(status_code=400, detail="Invalid session type")

    db = Database()
    with db.connection_context():
        session = ChatSession.get_or_none(user=user, session_type=session_type)
        if not session:
            return ChatActionResponse(success=True, message="No history to delete")

        # 删除该会话下的所有消息
        query = ChatMessage.delete().where(ChatMessage.session == session)
        query.execute()

        # 删除会话本身
        session.delete_instance()

        return ChatActionResponse(success=True, message="History deleted successfully")
