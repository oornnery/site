from __future__ import annotations

from sqlalchemy.ext.asyncio import create_async_engine

from apps.packages.config import settings


engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
