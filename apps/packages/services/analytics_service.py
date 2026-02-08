from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from apps.packages.domain.models import PageView


class AnalyticsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def hash_ip(ip: str | None) -> str | None:
        if not ip:
            return None
        return hashlib.sha256(ip.encode()).hexdigest()

    async def track_pageview(
        self,
        *,
        app_name: str,
        path: str,
        referrer: str | None,
        user_agent: str | None,
        ip: str | None,
    ) -> PageView:
        pageview = PageView(
            app=app_name,
            path=path,
            referrer=referrer,
            ua=user_agent,
            ip_hash=self.hash_ip(ip),
        )
        self.session.add(pageview)
        await self.session.commit()
        await self.session.refresh(pageview)
        return pageview

    async def pageviews_summary(self, *, days: int = 30) -> dict:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        total_result = await self.session.execute(
            select(func.count(PageView.id)).where(PageView.created_at >= start_date)
        )
        total = total_result.scalar() or 0

        by_app_result = await self.session.execute(
            select(PageView.app, func.count(PageView.id))
            .where(PageView.created_at >= start_date)
            .group_by(PageView.app)
        )
        by_app = {row[0]: row[1] for row in by_app_result.all()}

        top_paths_result = await self.session.execute(
            select(PageView.path, func.count(PageView.id).label("count"))
            .where(PageView.created_at >= start_date)
            .group_by(PageView.path)
            .order_by(func.count(PageView.id).desc())
            .limit(10)
        )
        top_paths = [{"path": row[0], "count": row[1]} for row in top_paths_result.all()]

        return {
            "period_days": days,
            "total_pageviews": total,
            "by_app": by_app,
            "top_paths": top_paths,
        }
