import asyncio
from tortoise import Tortoise
from app.core.config import settings

async def main():
    db_url = settings.MYSQL_URL
    print(f"Connecting to database...")
    await Tortoise.init(
        db_url=db_url,
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
    
    conn = Tortoise.get_connection("default")
    
    try:
        print("Executing ALTER TABLE resources DROP COLUMN file_url;")
        await conn.execute_query("ALTER TABLE resources DROP COLUMN file_url;")
        print("Successfully dropped file_url column.")
    except Exception as e:
        print(f"Failed to drop file_url column: {e}")

    try:
        print("Executing ALTER TABLE resources DROP COLUMN file_path;")
        await conn.execute_query("ALTER TABLE resources DROP COLUMN file_path;")
        print("Successfully dropped file_path column.")
    except Exception as e:
        print(f"Failed to drop file_path column: {e}")
        
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
