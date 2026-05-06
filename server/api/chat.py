import datetime
import re
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from server.database.connect import Database
from server.database.models import ChatMessage, ChatSession, MoodEntry, MoodType, User
from server.schema.chat import (
    ChatActionResponse,
    ChatHistoryData,
    ChatHistoryResponse,
    ChatMessageData,
    ChatResponse,
)
from server.utils.agent import chat_messages, create_conversation
from server.utils.auth import get_current_user
from server.utils.logger import log

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_type: str  # 'daily' or 'long-term'


class ChatActionRequest(BaseModel):
    session_type: str  # 'daily' or 'long-term'


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
        session, created = ChatSession.get_or_create(
            user_id=user, session_type=req.session_type
        )

        # 2. 如果没有 conversation_id，则在 Agent 端创建
        if not session.conversation_id:
            try:
                conv_id = create_conversation(str(user.username))
                session.conversation_id = conv_id
                session.save()
            except Exception as e:
                return ChatResponse(
                    success=False, code=500, message=f"创建 AI 会话失败: {str(e)}"
                )

        # 3. 保存用户消息
        ChatMessage.create(session_id=session, role="user", content=req.message)

        # 4. 调用 AI 模型生成回复
        try:
            response = chat_messages(
                conversation_id=session.conversation_id,
                user_id=str(user.username),
                message=req.message,
            )
            data = response.json()
            # 假设返回格式遵循 OpenAI 风格或者特定的 Agent 风格
            # 这里根据常见的结构进行初步解析，可能需要根据实际 API 调整
            ai_reply_content = data.get("answer", "抱歉，我暂时无法回答。")
        except Exception as e:
            ai_reply_content = f"AI 服务暂时不可用: {str(e)}"

        # 4.5. 检测 AI 回复是否包含 “当前情绪关键词：[情绪]” 格式的内容，并提取情绪关键词
        emotion_match = re.search(r"当前情绪关键词：\[(.*?)\]", ai_reply_content)
        if emotion_match:
            emotion_keyword = emotion_match.group(1)
            log.info(f"检测到情绪关键词: {emotion_keyword}")
            # 从回复中移除关键词部分
            ai_reply_content = re.sub(
                r"当前情绪关键词：\[.*?\]", "", ai_reply_content
            ).strip()

            # 保存当天的情绪
            try:
                mood_type = MoodType.get(MoodType.name == emotion_keyword)
                today = datetime.date.today()
                mood_entry, created = MoodEntry.get_or_create(
                    user_id=user,
                    log_date=today,
                    defaults={"mood_type_id": mood_type},
                )
                if not created:
                    mood_entry.mood_type_id = mood_type
                    mood_entry.save()
            except Exception as e:
                log.error(f"保存情绪失败: {str(e)}")

        # 5. 保存 AI 回复
        ai_message = ChatMessage.create(
            session_id=session, role="assistant", content=ai_reply_content
        )

        return ChatResponse(
            success=True,
            data=ChatMessageData(
                role=str(ai_message.role),
                content=str(ai_message.content),
                created_at=ai_message.created_at,  # type: ignore
            ),
        )


@router.get("/history", response_model=ChatHistoryResponse)
def history(
    req: ChatActionRequest = Depends(), user: Optional[User] = Depends(get_current_user)
) -> ChatHistoryResponse:
    """
    获取指定类型的聊天历史。
    """
    if not user:
        return ChatHistoryResponse(
            success=False, code=401, message="未授权或登录已过期"
        )

    if req.session_type not in ["daily", "long-term"]:
        return ChatHistoryResponse(success=False, code=400, message="非法的会话类型")

    db = Database()
    with db.connection_context():
        session = ChatSession.get_or_none(user_id=user, session_type=req.session_type)
        if not session:
            return ChatHistoryResponse(success=True, data=ChatHistoryData([]))

        messages = (
            ChatMessage.select()
            .where(ChatMessage.session_id == session)
            .order_by(ChatMessage.created_at.asc())
        )

        history_list = [
            ChatMessageData(role=m.role, content=m.content, created_at=m.created_at)
            for m in messages
        ]

        return ChatHistoryResponse(success=True, data=ChatHistoryData(history_list))


@router.post("/delete", response_model=ChatActionResponse)
def delete(
    req: ChatActionRequest, user: Optional[User] = Depends(get_current_user)
) -> ChatActionResponse:
    """
    删除指定类型的聊天历史。
    """
    if not user:
        return ChatActionResponse(success=False, code=401, message="未授权或登录已过期")

    if req.session_type not in ["daily", "long-term"]:
        return ChatActionResponse(success=False, code=400, message="非法的会话类型")

    db = Database()
    with db.connection_context():
        session = ChatSession.get_or_none(user_id=user, session_type=req.session_type)
        if not session:
            return ChatActionResponse(success=True, message="无历史记录可删除")

        # 删除该会话下的所有消息
        query = ChatMessage.delete().where(ChatMessage.session_id == session)
        query.execute()

        # 删除会话本身
        session.delete_instance()

        return ChatActionResponse(success=True, message="历史记录已成功删除")
