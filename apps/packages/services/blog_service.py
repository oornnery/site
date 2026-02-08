from __future__ import annotations

import re
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from apps.packages.content.markdown import render_markdown
from apps.packages.domain.models import Post, Reaction


class BlogService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_posts(
        self,
        *,
        category: str | None = None,
        tag: str | None = None,
        search: str | None = None,
        include_drafts: bool = False,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Post]:
        query = select(Post)
        if not include_drafts:
            query = query.where(Post.draft == False)  # noqa: E712
        if category:
            query = query.where(Post.category == category)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                col(Post.title).ilike(pattern)
                | col(Post.description).ilike(pattern)
                | col(Post.content_md).ilike(pattern)
            )

        query = query.order_by(col(Post.published_at).desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        posts = list(result.scalars().all())

        if tag:
            posts = [p for p in posts if p.tags and tag in p.tags]

        return posts

    async def get_post_by_slug(self, slug: str) -> Post | None:
        result = await self.session.execute(select(Post).where(Post.slug == slug))
        return result.scalar_one_or_none()

    async def get_post_by_id(self, post_id: UUID) -> Post | None:
        return await self.session.get(Post, post_id)

    async def create_post(self, data: dict) -> Post:
        post = Post(
            title=data["title"],
            slug=data["slug"],
            description=data.get("description", ""),
            content_md=data.get("content_md", ""),
            content_html=render_markdown(data.get("content_md", "")),
            image=data.get("image"),
            category=data.get("category", "general"),
            tags=data.get("tags", []),
            draft=data.get("draft", False),
            lang=data.get("lang", "pt"),
            reading_time=data.get("reading_time", self._calculate_reading_time(data.get("content_md", ""))),
        )
        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def update_post(self, post: Post, data: dict) -> Post:
        for field, value in data.items():
            if field == "content_md":
                post.content_md = value
                post.content_html = render_markdown(value)
            elif hasattr(post, field):
                setattr(post, field, value)
        post.updated_at = datetime.now(timezone.utc)
        if "content_md" in data and "reading_time" not in data:
            post.reading_time = self._calculate_reading_time(post.content_md)

        self.session.add(post)
        await self.session.commit()
        await self.session.refresh(post)
        return post

    async def delete_post(self, post: Post) -> None:
        await self.session.delete(post)
        await self.session.commit()

    async def increment_views(self, post: Post) -> None:
        post.views += 1
        self.session.add(post)
        await self.session.commit()

    async def get_categories_with_count(self) -> list[dict[str, int | str]]:
        result = await self.session.execute(
            select(Post.category, func.count(Post.id).label("count"))
            .where(Post.draft == False)  # noqa: E712
            .group_by(Post.category)
            .order_by(func.count(Post.id).desc())
        )
        return [{"category": row[0], "count": row[1]} for row in result.all()]

    async def get_tags_with_count(self) -> list[dict[str, int | str]]:
        posts = await self.get_posts(limit=500)
        counter: dict[str, int] = {}
        for post in posts:
            for tag in post.tags or []:
                counter[tag] = counter.get(tag, 0) + 1
        return [{"tag": tag, "count": count} for tag, count in sorted(counter.items())]

    async def add_reaction(self, post_id: UUID, reaction_type: str) -> Reaction:
        existing = await self.session.execute(
            select(Reaction).where(Reaction.post_id == post_id, Reaction.type == reaction_type)
        )
        reaction = existing.scalar_one_or_none()

        if reaction:
            reaction.count += 1
        else:
            reaction = Reaction(post_id=post_id, type=reaction_type, count=1)
            self.session.add(reaction)

        await self.session.commit()
        await self.session.refresh(reaction)
        return reaction

    async def get_reactions_count(self, post_id: UUID) -> dict[str, int]:
        result = await self.session.execute(select(Reaction.type, Reaction.count).where(Reaction.post_id == post_id))
        return {row[0]: row[1] for row in result.all()}

    @staticmethod
    def generate_slug(title: str) -> str:
        slug = title.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    def _calculate_reading_time(self, content: str) -> int:
        words = len(re.findall(r"\w+", content))
        return max(1, round(words / 200))
