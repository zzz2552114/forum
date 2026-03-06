from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.core.config import settings
from urllib.parse import urlparse

def init_db(app: FastAPI) -> None:
    # Use asyncmy driver explicitly
    db_url = settings.MYSQL_URL
    if db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "asyncmy://", 1)

    register_tortoise(
        app,
        db_url=db_url,
        modules={"models": [
            "app.models.user",
            "app.models.category",
            "app.models.forum",
            "app.models.resource",
            "app.models.report"
        ]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
