import importlib.util
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api.auth import router as auth_router
from server.api.chat import router as chat_router
from server.api.image import router as image_router
from server.api.letter import router as letter_router
from server.api.mood import router as mood_router
from server.api.user import router as user_router
from server.database.setup import setup as setup_database
from server.tasks.setup import setup as setup_tasks
from server.utils.logger import log

if not importlib.util.find_spec("server.secret"):
    log("app").error(
        "No secret.py found. Please create server/secret.py with necessary configurations."
    )
    raise ImportError("Missing server.secret module. Please create server/secret.py.")


# 生命周期事件：应用启动时初始化数据库
@asynccontextmanager
async def lifespan(app: FastAPI):
    log("app").info("Starting Lilac Backend API...")
    setup_database()
    tasks = setup_tasks()
    yield
    tasks.stop()
    log("app").info("Shutting down Lilac Backend API...")


# 初始化 FastAPI 应用
app = FastAPI(title="Lilac Backend API", lifespan=lifespan)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat System"])
app.include_router(image_router, prefix="/image", tags=["Image Resources"])
app.include_router(letter_router, prefix="/api/letter", tags=["Campus Letter"])
app.include_router(mood_router, prefix="/api/mood", tags=["Mood System"])
app.include_router(user_router, prefix="/api/user", tags=["User System"])


@app.get("/")
def read_root():
    return {"status": "online", "message": "Lilac Backend is running!"}
