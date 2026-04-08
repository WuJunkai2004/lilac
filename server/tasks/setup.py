import asyncio
import importlib
import random
from pathlib import Path
from typing import Callable

from server.tasks.register import TASKS
from server.utils.logger import log


def _discover_tasks():
    """
    自动发现并加载当前目录下的任务模块。
    通过动态导入触发各模块中的 @register 装饰器。
    """
    task_dir = Path(__file__).parent
    # 遍历当前目录下所有的 .py 文件
    for file_path in task_dir.glob("*.py"):
        module_name = file_path.stem

        # 排除掉本身的管理文件和初始化文件
        if module_name in ["setup", "register", "__init__"]:
            continue

        try:
            # 构造完整的导入路径，例如 server.task.clear_image
            # 假设项目根目录在 sys.path 中
            import_path = f"server.tasks.{module_name}"
            importlib.import_module(import_path)
            # 移除这里的 log，避免启动时输出过多，但在 register 里可以保留 log
        except Exception as e:
            log("task").error(f"Failed to auto-discover task '{module_name}': {e}")


async def _run_periodic_task(name: str, func: Callable):
    """
    通用周期任务执行器
    :param name: 任务名称
    :param func: 任务函数
    """
    # 随机化 3600 +/- 5 秒的初始等待时间，避免同时启动时的峰值负载
    # 如果任务在同一时刻执行，抖动也将在循环中生效
    base_interval = 3600
    jitter = random.randint(-5, 5)
    interval = base_interval + jitter

    log("task").info(f"Task '{name}' registered with interval: {interval}s")

    try:
        while True:
            # 释放控制权
            await asyncio.sleep(interval)
            # 再次生成抖动，使得下一次执行的时间点产生微调
            interval = base_interval + random.randint(-5, 5)
            # 使用 to_thread 运行同步阻塞代码，防止卡死 FastAPI 主线程
            await asyncio.to_thread(func)
    except asyncio.CancelledError:
        log("task").info(f"Task '{name}' stopped.")
    except Exception as e:
        log("task").error(f"Error in task '{name}': {e}")


class setup:
    def __init__(self):
        """
        初始化 setup 实例
        该实例在 server/main.py 的 lifespan 中被创建
        """
        # 1. 运行自动发现，填充 TASKS 字典
        _discover_tasks()

        # 2. 为 TASKS 中的每个函数创建 asyncio 任务
        self.tasks: list[asyncio.Task] = []
        for name, func in TASKS.items():
            self.tasks.append(asyncio.create_task(_run_periodic_task(name, func)))

    def stop(self):
        """
        停止所有后台定时任务
        该函数在 server/main.py 的 lifespan 中被调用
        """
        for task in self.tasks:
            task.cancel()
