import asyncio
from tortoise import Tortoise
from app.core.config import settings
from app.models.category import Space

async def run():
    print("Initiating DB connection...")
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
    
    # 查找 owner_id 为 None 的空间（这些通常是 seed 脚本生成的 mock 数据）
    # 如果用户自己建立的，必然有 owner_id
    mock_spaces = await Space.filter(owner_id__isnull=True).all()
    count = len(mock_spaces)
    print(f"Found {count} mock spaces without an owner.")
    
    if count > 0:
        for space in mock_spaces:
            # 删除级联关联的帖子等资源（如果 DB 未设置级联，代码级需要先删）
            # 当前 Tortoise ORM 外键应该已有级联或设置了限制，我们尝试直接删
            print(f"Deleting Space: {space.name} (ID: {space.id})")
            await space.delete()
        print("Mock spaces deleted.")
    else:
        print("No mock spaces found.")
        
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(run())
