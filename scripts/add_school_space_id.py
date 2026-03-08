import asyncio
from tortoise import Tortoise
from app.core.config import settings

async def main():
    db_url = settings.MYSQL_URL
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
        await conn.execute_query("ALTER TABLE resources ADD COLUMN school_space_id INT NULL;")
        print("1. Added school_space_id to resources table")
    except Exception as e:
        print(f"Failed to add column: {e}")
        
    try:    
        await conn.execute_query("ALTER TABLE resources ADD CONSTRAINT fk_res_school_space FOREIGN KEY (school_space_id) REFERENCES spaces (id) ON DELETE SET NULL;")
        print("2. Added foreign key constraint for school_space_id")
    except Exception as e:
        print(f"Failed to add constraint: {e}")

    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
