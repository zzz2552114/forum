import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from app.core.config import settings

async def run():
    await Tortoise.init(
        db_url=settings.MYSQL_URL,
        modules={"models": [
            "app.models.user", "app.models.category", "app.models.forum",
            "app.models.resource", "app.models.report", "app.models.interactions",
            "app.models.tag", "app.models.file", "app.models.notification"
        ]}
    )

    from app.models.resource import Resource
    from app.models.category import Space
    from app.models.forum import Post

    rs = await Resource.all()
    print(f"=== Resources ({len(rs)}) ===")
    for r in rs:
        print(f"  id={r.id} title={r.title} type={r.resource_type} space_id={r.space_id} school_space_id={r.school_space_id} status={r.status}")

    ss = await Space.all()
    print(f"\n=== Spaces ({len(ss)}) ===")
    for s in ss:
        print(f"  id={s.id} name={s.name} cat_id={s.category_id} owner={s.owner_id}")

    ps = await Post.all().prefetch_related("tags")
    print(f"\n=== Posts ({len(ps)}) ===")
    for p in ps:
        tags = [t.name for t in p.tags]
        print(f"  id={p.id} title={p.title} space_id={p.space_id} tags={tags}")

    await Tortoise.close_connections()

asyncio.run(run())
