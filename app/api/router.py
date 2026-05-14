from fastapi import APIRouter

from app.ai_mention.endpoint import router as ai_mention_router
from app.api.endpoints import (
    admin,
    auth,
    categories,
    comments,
    files,
    me,
    post_actions,
    posts,
    resources,
    search,
    spaces,
    tags,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(me.router, prefix="/me", tags=["me"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(spaces.router, prefix="/spaces", tags=["spaces"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(post_actions.router, prefix="/posts", tags=["post actions"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
api_router.include_router(ai_mention_router, prefix="/ai-mention", tags=["ai mention"])
