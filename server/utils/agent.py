import json
from typing import Any, Dict, Generator, Optional

import httpx

from server.utils.logger import log

TARGET_BASE = "https://agent.hit.edu.cn/api/proxy/api/v1"
API_KEY = "d7af895g77ds2k2ajae0"


class AgentClient:
    """
    单例模式的 Agent 客户端，复用 httpx.Client 实例。
    """

    _instance = None
    _client: httpx.Client

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 建立一个持久化的 client 实例，复用连接池
            cls._instance._client = httpx.Client(
                timeout=httpx.Timeout(30.0, read=300.0)
            )
        return cls._instance

    def _prepare_request(
        self, path: str, json_data: Optional[Dict[str, Any]], stream: bool
    ):
        """准备请求的基础配置，处理 URL、Headers 和 AppKey"""
        full_path = path if path.startswith("/") else f"/{path}"
        url = f"{TARGET_BASE}{full_path}"

        headers = {
            "Content-Type": "application/json",
            "Apikey": API_KEY,
            "Accept": "text/event-stream" if stream else "application/json",
        }

        data = (json_data or {}).copy()
        data["AppKey"] = API_KEY

        return url, headers, data

    def post(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """发送非流式 POST 请求"""
        url, headers, data = self._prepare_request(path, json_data, stream=False)
        log("agent").info(f"Sending POST request to {url}")

        try:
            resp = self._client.post(url, json=data, headers=headers, params=params)
            resp.raise_for_status()
            return resp
        except httpx.HTTPError as e:
            log("agent").error(f"HTTP error occurred: {e}")
            raise

    def stream(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Generator[bytes, None, None]:
        """发送流式 POST 请求"""
        url, headers, data = self._prepare_request(path, json_data, stream=True)
        log("agent").info(f"Sending streaming POST request to {url}")

        def sse_generator():
            # 使用 self._client.stream 以复用连接
            with self._client.stream(
                "POST", url, json=data, headers=headers, params=params
            ) as resp:
                resp.raise_for_status()
                yield from resp.iter_bytes()

        return sse_generator()


# 初始化全局单例实例
agent_client = AgentClient()


def _chat_query_v2_aggregated(
    url: str,
    headers: Dict[str, str],
    data: Dict[str, Any],
    params: Optional[Dict[str, Any]] = None,
) -> httpx.Response:
    """特殊处理：chat_query_v2 聚合流式响应以规避后端阻塞模式的不稳定性"""
    data["ResponseMode"] = "streaming"
    full_answer = ""
    # 使用单例的 client 实例进行流式请求并聚合
    with agent_client._client.stream(
        "POST", url, json=data, headers=headers, params=params
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if not line.startswith("data:"):
                continue
            data_str = line[5:].strip()
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
                full_answer += chunk.get("answer") or ""
            except Exception:
                continue

    mock_resp = httpx.Response(
        200, content=json.dumps({"answer": full_answer}).encode("utf-8")
    )
    mock_resp.request = httpx.Request("POST", url)
    return mock_resp


def create_conversation(user_id: str) -> str:
    """创建新会话"""
    try:
        resp = agent_client.post("/create_conversation", json_data={"UserID": user_id})
        data = resp.json()
        conv = data.get("Conversation", {})
        return conv.get("AppConversationID") or data.get("AppConversationID") or ""
    except Exception as e:
        log("agent").error(f"Failed to create conversation: {e}")
        return ""


def chat_messages(conversation_id: str, user_id: str, message: str) -> httpx.Response:
    """发送聊天请求（非流式，聚合结果）"""
    path = "/chat_query_v2"
    payload = {
        "UserID": user_id,
        "AppConversationID": conversation_id,
        "Query": message,
        "ResponseMode": "streaming",
    }
    url, headers, data = agent_client._prepare_request(path, payload, stream=False)
    return _chat_query_v2_aggregated(url, headers, data)


def chat_streamable(
    conversation_id: str, user_id: str, message: str
) -> Generator[bytes, None, None]:
    """发送聊天请求（流式）"""
    path = "/chat_query_v2"
    payload = {
        "UserID": user_id,
        "AppConversationID": conversation_id,
        "Query": message,
        "ResponseMode": "streaming",
    }
    return agent_client.stream(path, json_data=payload)
