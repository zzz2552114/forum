import asyncio
from tortoise import Tortoise
from app.core.config import settings
from app.models.category import Space, Category

async def cleanup():
    await Tortoise.init(
        db_url=settings.DATABASE_URL,
        modules={"models": ["app.models.user", "app.models.category", "app.models.forum", "app.models.resource", "app.models.file", "app.models.tag"]}
    )
    
    # Delete spaces with unneeded names
    spaces = await Space.all()
    for space in spaces:
        if space.name.startswith("Action Space") or space.name.startswith("Search Space") or "Cat " in space.name:
            await space.delete()
            print(f"Deleted space: {space.name}")
            
    cats = await Category.all()
    for cat in cats:
        if cat.name not in ["学校", "课程", "专业", "休闲娱乐", "探索"]:
            await cat.delete()
            print(f"Deleted cat: {cat.name}")

    print("Cleanup complete.")
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(cleanup())
