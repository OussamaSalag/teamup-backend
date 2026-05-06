from __future__ import annotations

import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, engine
from app.models.user import Skill

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Skill seed data
# ---------------------------------------------------------------------------

SKILLS: list[dict[str, str]] = [
    # Programming
    {"name": "Python", "category": "Programming"},
    {"name": "JavaScript", "category": "Programming"},
    {"name": "TypeScript", "category": "Programming"},
    {"name": "Java", "category": "Programming"},
    {"name": "C++", "category": "Programming"},
    {"name": "React", "category": "Programming"},
    {"name": "FastAPI", "category": "Programming"},
    {"name": "Node.js", "category": "Programming"},
    # Design
    {"name": "UI/UX Design", "category": "Design"},
    {"name": "Figma", "category": "Design"},
    {"name": "Adobe XD", "category": "Design"},
    # Data
    {"name": "Machine Learning", "category": "Data"},
    {"name": "Data Analysis", "category": "Data"},
    {"name": "SQL", "category": "Data"},
    # Other
    {"name": "Project Management", "category": "Other"},
    {"name": "DevOps", "category": "Other"},
    {"name": "Docker", "category": "Other"},
    {"name": "Git", "category": "Other"},
]


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------

async def seed_skills(db: AsyncSession) -> None:
    """Insert skills that don't already exist, keyed by name."""
    inserted = 0
    for skill_data in SKILLS:
        result = await db.execute(
            select(Skill).where(Skill.name == skill_data["name"])
        )
        existing = result.scalar_one_or_none()
        if existing is None:
            db.add(Skill(name=skill_data["name"], category=skill_data["category"]))
            inserted += 1

    await db.commit()
    logger.info("Seed complete: %d new skills inserted.", inserted)


async def seed_db() -> None:
    """Bootstrap the database with all seed data."""
    async with AsyncSessionLocal() as db:
        await seed_skills(db)
    await engine.dispose()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_db())
