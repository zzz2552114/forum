import asyncio
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from app.core.config import settings

# Real space IDs that belong to the user
REAL_SPACE_IDS = {47, 72, 73, 74, 75, 83}

async def run():
    await Tortoise.init(
        db_url=settings.MYSQL_URL,
        modules={"models": [
            "app.models.user", "app.models.category", "app.models.forum",
            "app.models.resource", "app.models.report", "app.models.interactions",
            "app.models.tag", "app.models.file", "app.models.notification"
        ]}
    )

    from app.models.category import Space
    from app.models.forum import Post

    # Delete all test spaces (not in the real set)
    test_spaces = await Space.filter(id__not_in=list(REAL_SPACE_IDS))
    print(f"Deleting {len(test_spaces)} test spaces...")
    for s in test_spaces:
        print(f"  Deleting space: id={s.id} name={s.name}")
    deleted_spaces = await Space.filter(id__not_in=list(REAL_SPACE_IDS)).delete()
    print(f"Deleted {deleted_spaces} test spaces.")

    # Delete all test posts (not in real spaces)
    test_posts = await Post.filter(space_id__not_in=list(REAL_SPACE_IDS))
    print(f"\nDeleting {len(test_posts)} test posts...")
    deleted_posts = await Post.filter(space_id__not_in=list(REAL_SPACE_IDS)).delete()
    print(f"Deleted {deleted_posts} test posts.")

    # Verify remaining
    remaining_spaces = await Space.all()
    remaining_posts = await Post.all().prefetch_related("tags")
    print(f"\n=== Remaining Spaces ({len(remaining_spaces)}) ===")
    for s in remaining_spaces:
        print(f"  id={s.id} name={s.name}")
    print(f"\n=== Remaining Posts ({len(remaining_posts)}) ===")
    for p in remaining_posts:
        tags = [t.name for t in p.tags]
        print(f"  id={p.id} title={p.title} space_id={p.space_id} tags={tags}")

    await Tortoise.close_connections()

asyncio.run(run())
