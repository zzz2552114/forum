from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from app.core.config import settings
from urllib.parse import urlparse

def init_db(app: FastAPI) -> None:
    # Use asyncmy driver by leaving it as mysql://
    db_url = settings.MYSQL_URL

    register_tortoise(
        app,
        config={
            "connections": {"default": db_url},
            "apps": {
                "models": {
                    "models": [
                        "app.models.user",
                        "app.models.category",
                        "app.models.forum",
                        "app.models.resource",
                        "app.models.report",
                        "app.models.interactions",
                        "app.models.tag",
                        "app.models.file",
                        "app.models.notification"
                    ],
                    "default_connection": "default",
                }
            },
            "use_tz": False,
        },
        generate_schemas=True,
        add_exception_handlers=True,
    )
