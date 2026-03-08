import asyncio
from tortoise import Tortoise
from app.core.config import settings
from app.models.category import Category

async def seed():
    await Tortoise.init(
        db_url=settings.MYSQL_URL,
        modules={"models": [
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
    
    categories = ["学校", "课程", "专业", "休闲娱乐", "探索"]
    for c_name in categories:
        await Category.get_or_create(name=c_name)
        print(f"Ensured category: {c_name}")
        
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(seed())
