from __future__ import annotations

from sqlalchemy import func
from sqlmodel import select

from apps.packages.config import settings
from apps.packages.db.session import async_session_factory
from apps.packages.content.markdown import render_markdown
from apps.packages.domain.models import Comment, Post, Profile, Project, Settings, User
from apps.packages.security import get_password_hash


async def seed_db() -> None:
    if not settings.SEED_DB_ON_STARTUP:
        return

    async with async_session_factory() as session:
        default_about_summary = "Building reliable web products with Python, FastAPI, and SSR-first UX."
        default_about_markdown = (
            "Experienced full-stack developer building SSR-first applications. "
            "Focused on clean architecture, performance, and pragmatic UX."
        )

        admin = (await session.execute(select(User).where(User.email == "admin@example.com"))).scalar_one_or_none()
        if not admin:
            admin = User(
                email="admin@example.com",
                name="Fabio Souza",
                hashed_password=get_password_hash("admin123"),
                is_admin=True,
                role="admin",
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)

        profile = (await session.execute(select(Profile).where(Profile.user_id == admin.id))).scalar_one_or_none()
        if not profile:
            profile = Profile(
                user_id=admin.id,
                name="Fabio Souza",
                location="São Paulo, Brazil",
                short_bio="Full-stack Developer",
                email="fabiohcsouza@outlook.com.br",
                github="oornnery",
                linkedin="fabiohcsouza",
                about_summary=default_about_summary,
                about_markdown=default_about_markdown,
                skills=["Python", "FastAPI", "JX", "HTMX", "Alpine.js"],
                social_links=[
                    {"title": "Email", "url": "fabiohcsouza@outlook.com.br", "icon": "email"},
                    {"title": "GitHub", "url": "oornnery", "icon": "github"},
                    {"title": "LinkedIn", "url": "fabiohcsouza", "icon": "linkedin"},
                    {"title": "X", "url": "oornnery", "icon": "x"},
                ],
            )
            session.add(profile)
        else:
            updated = False
            if not profile.about_markdown:
                profile.about_markdown = default_about_markdown
                updated = True
            if not profile.about_summary:
                if profile.about_markdown:
                    first_line = profile.about_markdown.splitlines()[0].strip()
                    profile.about_summary = first_line or default_about_summary
                else:
                    profile.about_summary = default_about_summary
                updated = True
            if not profile.skills:
                profile.skills = ["Python", "FastAPI", "JX", "HTMX", "Alpine.js"]
                updated = True
            if not profile.social_links:
                profile.social_links = [
                    {"title": "Email", "url": profile.email, "icon": "email"},
                    {"title": "GitHub", "url": profile.github or "oornnery", "icon": "github"},
                    {"title": "LinkedIn", "url": profile.linkedin or "fabiohcsouza", "icon": "linkedin"},
                    {"title": "X", "url": profile.twitter or "oornnery", "icon": "x"},
                ]
                updated = True
            if not profile.work_experience:
                profile.work_experience = [
                    {
                        "title": "Senior Full-stack Developer",
                        "company": "Independent",
                        "location": "São Paulo, Brazil",
                        "start_date": "2021",
                        "end_date": "Present",
                        "description": "Building SSR-first products with FastAPI, HTMX, and modern design systems.",
                    },
                    {
                        "title": "Software Engineer",
                        "company": "Telecom & SaaS",
                        "location": "Remote",
                        "start_date": "2017",
                        "end_date": "2021",
                        "description": "Delivered APIs, dashboards, and internal tooling at scale.",
                    },
                ]
                updated = True
            if not profile.education:
                profile.education = [
                    {
                        "school": "Universidade",
                        "degree": "BSc Computer Science",
                        "start_date": "2012",
                        "end_date": "2016",
                    }
                ]
                updated = True
            if not profile.certificates:
                profile.certificates = [
                    {
                        "name": "AWS Certified Developer",
                        "issuer": "Amazon",
                        "date": "2020",
                        "url": "https://aws.amazon.com/certification/",
                        "credential_id": "AWS-DEV-0000",
                    }
                ]
                updated = True
            if not profile.social_links:
                profile.social_links = [
                    {"label": "Email", "url": "mailto:fabiohcsouza@outlook.com.br", "icon": "email"},
                    {"label": "GitHub", "url": "https://github.com/oornnery", "icon": "github"},
                    {"label": "LinkedIn", "url": "https://linkedin.com/in/fabiohcsouza", "icon": "linkedin"},
                    {"label": "X", "url": "https://x.com/oornnery", "icon": "twitter"},
                ]
                updated = True
            if updated:
                session.add(profile)

        app_settings = (await session.execute(select(Settings).where(Settings.id == 1))).scalar_one_or_none()
        if not app_settings:
            app_settings = Settings(
                id=1,
                site_name="Fabio Souza",
                projects_enabled=True,
                blog_enabled=True,
                home_background_url="https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1600&q=80",
                home_projects_count=4,
                home_posts_count=4,
                home_projects_featured_only=False,
            )
            session.add(app_settings)
        elif not app_settings.home_background_url:
            app_settings.home_background_url = (
                "https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=1600&q=80"
            )
            session.add(app_settings)
        if app_settings.home_projects_count is None:
            app_settings.home_projects_count = 4
            session.add(app_settings)
        if app_settings.home_posts_count is None:
            app_settings.home_posts_count = 4
            session.add(app_settings)
        if app_settings.home_projects_featured_only is None:
            app_settings.home_projects_featured_only = False
            session.add(app_settings)

        post_count = (await session.execute(select(func.count(Post.id)))).scalar() or 0
        if post_count < 6:
            existing = {
                row[0] for row in (await session.execute(select(Post.slug))).all() if row[0]
            }
            posts_seed = [
                {
                    "title": "Welcome to the Blog",
                    "slug": "welcome-to-the-blog",
                    "description": "First post in the new multi-app architecture.",
                    "content_md": "# Welcome\n\nThis is the first post in the new blog.",
                    "category": "tech",
                    "tags": ["fastapi", "jx"],
                    "reading_time": 2,
                },
                {
                    "title": "SSR-first UX with JX + HTMX",
                    "slug": "ssr-first-ux-jx-htmx",
                    "description": "Why server-first interaction still wins for personal sites.",
                    "content_md": "## SSR-first\n\nFast pages, simple state, and predictable UX.",
                    "category": "web",
                    "tags": ["htmx", "ssr", "jx"],
                    "reading_time": 4,
                },
                {
                    "title": "Design tokens and motion",
                    "slug": "design-tokens-and-motion",
                    "description": "Keeping UI consistent with tokens and motion primitives.",
                    "content_md": "## Tokens\n\nColor, spacing, and motion create a shared language.",
                    "category": "design",
                    "tags": ["design-system", "tokens"],
                    "reading_time": 3,
                },
                {
                    "title": "FastAPI patterns for monorepos",
                    "slug": "fastapi-monorepo-patterns",
                    "description": "Sharing services and models across multiple apps.",
                    "content_md": "## Monorepo\n\nShared packages reduce duplication and drift.",
                    "category": "backend",
                    "tags": ["fastapi", "sqlmodel"],
                    "reading_time": 5,
                },
                {
                    "title": "HTMX partials done right",
                    "slug": "htmx-partials-done-right",
                    "description": "Patterns for reusable partials and clean router design.",
                    "content_md": "## Partials\n\nSmall, composable endpoints keep pages fast.",
                    "category": "web",
                    "tags": ["htmx", "frontend"],
                    "reading_time": 4,
                },
            ]
            for item in posts_seed:
                if item["slug"] in existing:
                    continue
                session.add(
                    Post(
                        title=item["title"],
                        slug=item["slug"],
                        description=item["description"],
                        content_md=item["content_md"],
                        content_html=render_markdown(item["content_md"]),
                        category=item["category"],
                        tags=item["tags"],
                        draft=False,
                        reading_time=item["reading_time"],
                    )
                )

        comment_count = (await session.execute(select(func.count(Comment.id)))).scalar() or 0
        if comment_count < 4:
            posts = (await session.execute(select(Post).limit(3))).scalars().all()
            for post in posts:
                session.add(
                    Comment(
                        post_id=post.id,
                        content="Great post. Clear and practical.",
                        guest_name="Reader",
                        guest_email="reader@example.com",
                    )
                )

        project_count = (await session.execute(select(func.count(Project.id)))).scalar() or 0
        if project_count < 6:
            existing = {
                row[0] for row in (await session.execute(select(Project.slug))).all() if row[0]
            }
            projects_seed = [
                {
                    "title": "Portfolio Platform",
                    "slug": "portfolio-platform",
                    "description": "SSR-first monorepo with FastAPI + JX.",
                    "content_md": "# Portfolio Platform\n\nFast, clean, and scalable.",
                    "category": "web",
                    "tech_stack": ["Python", "FastAPI", "JX"],
                    "featured": True,
                    "github_url": "https://github.com/oornnery",
                },
                {
                    "title": "Blog Engine",
                    "slug": "blog-engine",
                    "description": "Markdown-driven blog with tags, search and RSS.",
                    "content_md": "# Blog Engine\n\nBuilt with HTMX and SSR.",
                    "category": "web",
                    "tech_stack": ["HTMX", "Jinja", "FastAPI"],
                    "featured": True,
                },
                {
                    "title": "Admin Console",
                    "slug": "admin-console",
                    "description": "Secure CRUD dashboard for content and analytics.",
                    "content_md": "# Admin Console\n\nSimple workflows, fast actions.",
                    "category": "backend",
                    "tech_stack": ["FastAPI", "SQLModel", "Alpine.js"],
                    "featured": False,
                },
                {
                    "title": "Design System",
                    "slug": "design-system",
                    "description": "Reusable UI kit with tokens, motion and components.",
                    "content_md": "# Design System\n\nConsistency across apps.",
                    "category": "design",
                    "tech_stack": ["CSS", "JX", "Tailwind"],
                    "featured": False,
                },
                {
                    "title": "Analytics Lite",
                    "slug": "analytics-lite",
                    "description": "Pageview tracking with minimal overhead.",
                    "content_md": "# Analytics Lite\n\nTrack what matters.",
                    "category": "data",
                    "tech_stack": ["Postgres", "Python"],
                    "featured": False,
                },
            ]
            for item in projects_seed:
                if item["slug"] in existing:
                    continue
                session.add(
                    Project(
                        title=item["title"],
                        slug=item["slug"],
                        description=item["description"],
                        content_md=item["content_md"],
                        content_html=render_markdown(item["content_md"]),
                        category=item["category"],
                        tech_stack=item["tech_stack"],
                        featured=item.get("featured", False),
                        github_url=item.get("github_url"),
                        demo_url=item.get("demo_url"),
                    )
                )

        await session.commit()
