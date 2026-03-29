from contextlib import asynccontextmanager

from fastapi import FastAPI

from server.api.auth import router as auth_router
from server.api.chat import router as chat_router
from server.api.image import router as image_router
from server.api.user import router as user_router
from server.database.setup import setup
from server.utils.logger import log


# 生命周期事件：应用启动时初始化数据库
@asynccontextmanager
async def lifespan(app: FastAPI):
    log("app").info("Starting Lilac Backend API...")
    setup()
    yield
    log("app").info("Shutting down Lilac Backend API...")


# 初始化 FastAPI 应用
app = FastAPI(title="Lilac Backend API", lifespan=lifespan)

# 挂载路由
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat System"])
app.include_router(image_router, prefix="/image", tags=["Image Resources"])
app.include_router(user_router, prefix="/api/user", tags=["User System"])


@app.get("/")
def read_root():
    return {"status": "online", "message": "Lilac Backend is running!"}
