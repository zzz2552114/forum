import asyncio
from tortoise import Tortoise
from app.core.config import settings
from app.models.resource import Resource

async def clear_resources():
    await Tortoise.init(
        db_url=settings.MYSQL_URL,
        modules={'models': [
            "app.models.user",
            "app.models.category",
            "app.models.forum",
            "app.models.resource",
            "app.models.report",
            "app.models.interactions",
            "app.models.tag",
            "app.models.file",
            "app.models.notification"
        ]}
    )
    deleted = await Resource.all().delete()
    print(f"Deleted {deleted} resources from database.")
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(clear_resources())
