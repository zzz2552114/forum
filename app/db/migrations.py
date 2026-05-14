from __future__ import annotations

from loguru import logger
from tortoise import Tortoise

from app.models.enums import TrustLevel, UserRole
from app.models.user import User


async def migrate_user_roles_and_trust() -> None:
    """Idempotent data cleanup for the new authorization model."""

    conn = Tortoise.get_connection("default")
    table = User._meta.db_table
    basic_trust = int(TrustLevel.BASIC)
    user_role = UserRole.USER.value

    # Use raw SQL here because "master" is no longer a valid enum value and
    # ORM enum casting would reject the legacy rows before we can migrate them.
    master_demoted, _ = await conn.execute_query(
        f"UPDATE {table} "
        f"SET role='{user_role}', trust_level={basic_trust} "
        "WHERE role='master'"
    )

    valid_roles = [role.value for role in UserRole]
    invalid_roles_fixed = await User.exclude(role__in=valid_roles).update(role=UserRole.USER)

    low_trust_fixed = await User.filter(trust_level__lt=int(TrustLevel.GUEST)).update(
        trust_level=TrustLevel.BASIC,
    )
    high_trust_fixed = await User.filter(trust_level__gt=int(TrustLevel.CONTRIBUTOR)).update(
        trust_level=TrustLevel.BASIC,
    )

    guest_users_promoted = await User.filter(role=UserRole.USER, trust_level=TrustLevel.GUEST).update(
        trust_level=TrustLevel.BASIC,
    )

    if any([master_demoted, invalid_roles_fixed, low_trust_fixed, high_trust_fixed, guest_users_promoted]):
        logger.info(
            "Authz migration applied: demoted_master={}, fixed_roles={}, low_trust={}, high_trust={}, promoted_guest_users={}",
            master_demoted,
            invalid_roles_fixed,
            low_trust_fixed,
            high_trust_fixed,
            guest_users_promoted,
        )
