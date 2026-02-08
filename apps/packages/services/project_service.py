from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from apps.packages.content.markdown import render_markdown
from apps.packages.domain.models import Project


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_projects(
        self,
        *,
        category: str | None = None,
        featured: bool | None = None,
        search: str | None = None,
        tech: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Project]:
        query = select(Project)
        if category:
            query = query.where(Project.category == category)
        if featured is not None:
            query = query.where(Project.featured == featured)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                col(Project.title).ilike(pattern)
                | col(Project.description).ilike(pattern)
                | col(Project.content_md).ilike(pattern)
            )
        query = query.order_by(col(Project.created_at).desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        projects = list(result.scalars().all())
        if tech:
            tech_lower = tech.lower()
            projects = [
                p for p in projects if any(tech_lower in t.lower() for t in (p.tech_stack or []))
            ]
        return projects

    async def get_featured_projects(self, limit: int = 3) -> list[Project]:
        return await self.get_projects(featured=True, limit=limit)

    async def get_project_by_slug(self, slug: str) -> Project | None:
        result = await self.session.execute(select(Project).where(Project.slug == slug))
        return result.scalar_one_or_none()

    async def get_project_by_id(self, project_id: UUID) -> Project | None:
        return await self.session.get(Project, project_id)

    async def create_project(self, data: dict) -> Project:
        project = Project(
            title=data["title"],
            slug=data["slug"],
            description=data.get("description", ""),
            content_md=data.get("content_md", ""),
            content_html=render_markdown(data.get("content_md", "")),
            image=data.get("image"),
            tech_stack=data.get("tech_stack", []),
            category=data.get("category", "other"),
            github_url=data.get("github_url"),
            demo_url=data.get("demo_url"),
            featured=data.get("featured", False),
        )
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def update_project(self, project: Project, data: dict) -> Project:
        for field, value in data.items():
            if field == "content_md":
                project.content_md = value
                project.content_html = render_markdown(value)
            elif hasattr(project, field):
                setattr(project, field, value)

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete_project(self, project: Project) -> None:
        await self.session.delete(project)
        await self.session.commit()

    async def get_categories(self) -> list[str]:
        result = await self.session.execute(select(Project.category).distinct())
        return [row[0] for row in result.all() if row[0]]
