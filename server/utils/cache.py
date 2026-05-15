import contextvars
import time
from datetime import date
from functools import wraps
from threading import Lock
from typing import Any, Callable, Dict, Optional, Tuple

# 上下文变量，用于在装饰器和 init 之间同步缓存状态
_current_cache_key = contextvars.ContextVar("_current_cache_key", default=None)
_current_cache_options = contextvars.ContextVar("_current_cache_options", default=None)
_current_cache_object = contextvars.ContextVar("_current_cache_object", default=None)


class MemoryCache:
    """
    轻量级显式内存缓存工具类
    """

    def __init__(self):
        # 存储结构: { key: (value, expiry_timestamp, created_date or None) }
        self._cache: Dict[str, Tuple[Any, float, Optional[date]]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存。
        :param key: 唯一键值
        :return: 缓存的数据或 None（如果不存在、已过期或日期已切换）
        """
        with self._lock:
            if key not in self._cache:
                return None

            value, expiry, created_date = self._cache[key]
            now = time.time()

            # 检查 TTL 过期
            if now >= expiry:
                del self._cache[key]
                return None

            # 检查日期切换 (only_today 逻辑)
            if created_date is not None and created_date != date.today():
                del self._cache[key]
                return None

            return value

    def set(
        self, key: str, value: Any, ttl: int = 3600, only_today: bool = False
    ) -> None:
        """
        设置缓存。
        :param key: 唯一键值
        :param value: 要存储的数据
        :param ttl: 有效期（秒），默认 1 小时
        :param only_today: 如果为 True，则在日期跨过午夜零点时自动失效
        """
        now = time.time()
        created_date = date.today() if only_today else None

        with self._lock:
            self._cache[key] = (value, now + ttl, created_date)

    def delete(self, key: str) -> None:
        """删除指定缓存"""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()

    def init(self, default: Any) -> Tuple[Any, bool]:
        """
        显式初始化或获取缓存。配合 enable 装饰器使用。
        :param default: 缓存不存在时的默认值（通常是 mutable 对象如 Counter()）
        :return: (缓存对象, 是否命中缓存)
        """
        key = _current_cache_key.get()
        if not key:
            # 如果不在装饰器上下文中，回退到非缓存模式
            return default, False

        cached_val = self.get(key)
        if cached_val is not None:
            return cached_val, True

        # 缓存未命中，将默认对象标记为待存入
        _current_cache_object.set(default)
        return default, False

    def enable(self, expire: int = 3600, only_today: bool = False):
        """
        装饰器：为函数建立显式缓存上下文。
        :param expire: 过期时间（秒）
        :param only_today: 是否仅当天有效（跨零点失效）
        """

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 1. 生成唯一 Key
                key = self._generate_key(func, args, kwargs)

                # 2. 设置上下文
                token_key = _current_cache_key.set(key)  # type: ignore
                token_opts = _current_cache_options.set(
                    {"expire": expire, "only_today": only_today}  # type: ignore
                )
                token_obj = _current_cache_object.set(None)

                try:
                    # 3. 执行函数
                    result = func(*args, **kwargs)

                    # 4. 函数结束后，如果有待存储的对象（即 init 被调用且未命中），则存入缓存
                    obj_to_cache = _current_cache_object.get()
                    if obj_to_cache is not None:
                        self.set(key, obj_to_cache, ttl=expire, only_today=only_today)

                    return result
                finally:
                    # 5. 还原上下文
                    _current_cache_key.reset(token_key)
                    _current_cache_options.reset(token_opts)
                    _current_cache_object.reset(token_obj)

            return wrapper

        return decorator

    def _generate_key(self, func: Callable, args: Tuple, kwargs: Dict) -> str:
        """生成基于函数签名和参数的唯一键"""
        parts = [func.__module__, func.__name__]
        # 序列化位置参数
        for arg in args:
            parts.append(self._serialize(arg))
        # 序列化关键字参数
        for k, v in sorted(kwargs.items()):
            parts.append(f"{k}={self._serialize(v)}")
        return ":".join(parts)

    def _serialize(self, obj: Any) -> str:
        """简单序列化，支持 Pydantic 模型"""
        if hasattr(obj, "model_dump"):
            return str(obj.model_dump())
        if hasattr(obj, "dict"):
            return str(obj.dict())
        return str(obj)


# 全局单例
cache = MemoryCache()
