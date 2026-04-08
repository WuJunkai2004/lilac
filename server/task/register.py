from typing import Callable, Dict

# 全局任务注册表
TASKS: Dict[str, Callable] = {}


def register(name: str):
    """
    任务注册装饰器
    :param name: 任务唯一标识名称
    """

    def decorator(func: Callable):
        TASKS[name] = func
        return func

    return decorator
