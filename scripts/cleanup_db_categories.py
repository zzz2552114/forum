import asyncio
from tortoise import Tortoise
from app.core.config import settings
from app.models.category import Category, Space

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
    
    allowed = ['学校', '课程', '休闲娱乐', '专业', '探索']
    
    # Ensure allowed categories exist
    allowed_categories = {}
    for name in allowed:
        cat, _ = await Category.get_or_create(name=name, defaults={"description": f"{name}模块"})
        allowed_categories[name] = cat
        
    fallback_cat = allowed_categories['探索']
    
    print("Normalizing spaces and categories...")
    
    # Get all categories
    all_cats = await Category.all()
    
    for cat in all_cats:
        if cat.name not in allowed:
            print(f"Processing category '{cat.name}' (ID: {cat.id})")
            
            # Find and move spaces to the fallback category
            spaces = await Space.filter(category_id=cat.id)
            for space in spaces:
                space.category_id = fallback_cat.id
                await space.save(update_fields=["category_id"])
                print(f"  Moved space '{space.name}' to '探索'")
                
            # Delete the category
            await cat.delete()
            print(f"  Deleted category '{cat.name}'")

    print("Database normalization complete.")
    await Tortoise.close_connections()

if __name__ == "__main__":
    asyncio.run(main())
