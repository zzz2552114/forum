import asyncio
import uuid

from fastapi.testclient import TestClient
from tortoise import Tortoise

from app.db.migrations import migrate_user_roles_and_trust
from app.models.enums import TrustLevel, UserRole
from app.models.user import User
from main import app


def test_master_role_rows_are_demoted_to_user_basic():
    with TestClient(app) as client:
        username = f"legacy_master_{uuid.uuid4().hex[:8]}"
        register = client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@example.com",
                "password": "testpassword123",
            },
        )
        assert register.status_code == 200

        async def mark_as_legacy_master() -> None:
            conn = Tortoise.get_connection("default")
            table = User._meta.db_table
            await conn.execute_query(
                f"UPDATE {table} SET role='master', trust_level=0 WHERE username='{username}'"
            )

        asyncio.run(mark_as_legacy_master())

        asyncio.run(migrate_user_roles_and_trust())

        async def read_user() -> User:
            return await User.get(username=username)

        migrated = asyncio.run(read_user())
        assert migrated.role == UserRole.USER
        assert int(migrated.trust_level) == int(TrustLevel.BASIC)

        # Re-run to verify idempotence
        asyncio.run(migrate_user_roles_and_trust())
        migrated_again = asyncio.run(read_user())
        assert migrated_again.role == UserRole.USER
        assert int(migrated_again.trust_level) == int(TrustLevel.BASIC)
