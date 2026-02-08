from __future__ import annotations

from sqlmodel import SQLModel

from apps.packages.db.engine import engine


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

        if conn.dialect.name == "sqlite":
            result = await conn.exec_driver_sql("PRAGMA table_info(profile)")
            profile_columns = {row[1] for row in result}
            if "social_links" not in profile_columns:
                await conn.exec_driver_sql("ALTER TABLE profile ADD COLUMN social_links JSON")
            if "about_summary" not in profile_columns:
                await conn.exec_driver_sql("ALTER TABLE profile ADD COLUMN about_summary TEXT DEFAULT ''")

            result = await conn.exec_driver_sql("PRAGMA table_info(settings)")
            columns = {row[1] for row in result}
            if "home_projects_count" not in columns:
                await conn.exec_driver_sql(
                    "ALTER TABLE settings ADD COLUMN home_projects_count INTEGER DEFAULT 4"
                )
            if "home_posts_count" not in columns:
                await conn.exec_driver_sql(
                    "ALTER TABLE settings ADD COLUMN home_posts_count INTEGER DEFAULT 4"
                )
            if "home_projects_featured_only" not in columns:
                await conn.exec_driver_sql(
                    "ALTER TABLE settings ADD COLUMN home_projects_featured_only BOOLEAN DEFAULT 0"
                )
