from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.ai_mention.endpoint import websocket_router as ai_notification_ws_router
from app.api.router import api_router
from app.core.config import settings
from app.core.responses import error_response
from app.db.connection import init_db
from app.db.migrations import migrate_user_roles_and_trust
from app.realtime_chat.endpoint import router as realtime_chat_router

# Configure loguru
logger.remove()
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db.migrations import init_super_root
    from app.core.trending import sync_all_hot_scores_task
    import asyncio
    
    await migrate_user_roles_and_trust()
    await init_super_root()
    
    # --- 启动后台守护任务 ---
    trending_task = asyncio.create_task(sync_all_hot_scores_task())
    
    yield
    
    trending_task.cancel()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(realtime_chat_router)
app.include_router(ai_notification_ws_router)

init_db(app)


@app.get("/health", tags=["health"])
async def health_check():
    from app.core.responses import success_response

    return success_response({"status": "ok"})


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        if "code" in exc.detail and "message" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                code=exc.status_code,
                message=exc.detail.get("message", "request failed"),
                data=exc.detail.get("data"),
            ),
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(code=exc.status_code, message=str(exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=error_response(code=40001, message="invalid request", data=exc.errors()),
    )
