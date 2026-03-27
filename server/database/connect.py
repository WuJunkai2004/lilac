from pathlib import Path
from typing import Optional

from peewee import SqliteDatabase

from server.utils.logger import log


class _Database:
    """基于类的单例模式管理数据库连接"""

    _instance: Optional[SqliteDatabase] = None
    _db_path: Path = Path(__file__).parent.parent.parent / "datas" / "lilac.db"

    @classmethod
    def get_db(cls) -> SqliteDatabase:
        """
        核心单例获取方法。
        每次调用都会返回同一个 SqliteDatabase 实例。
        """
        if cls._instance is None:
            # 确保目录存在
            cls._db_path.parent.mkdir(parents=True, exist_ok=True)
            # 初始化 Peewee 数据库对象
            cls._instance = SqliteDatabase(str(cls._db_path))
            log("database").info(f"Initialized database at {cls._db_path}")
        return cls._instance

    @classmethod
    def reset(cls, path: Path):
        """允许在初始化前更改数据库路径"""
        cls._db_path = path
        cls._instance = None  # 重置实例以应用新路径


def Database() -> SqliteDatabase:
    """外部调用接口，返回数据库实例"""
    return _Database.get_db()
