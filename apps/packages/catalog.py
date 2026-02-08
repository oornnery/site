from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from jx import Catalog

from apps.packages.config import settings
from apps.packages.content.markdown import render_markdown

UI_DIR = Path(__file__).resolve().parent
UI_COMPONENTS_DIR = UI_DIR / "components"


def build_catalog(*, app_components_dir: Path | None = None, debug: bool = False, **globals: Any) -> Catalog:
    globals.setdefault("current_year", datetime.now().year)
    globals.setdefault("settings", settings)
    globals.setdefault("PUBLIC_PORTFOLIO_URL", settings.PUBLIC_PORTFOLIO_URL)
    globals.setdefault("PUBLIC_BLOG_URL", settings.PUBLIC_BLOG_URL)
    globals.setdefault("PUBLIC_ADMIN_URL", settings.PUBLIC_ADMIN_URL)

    catalog = Catalog(auto_reload=debug, **globals)

    # App-level components are loaded first so they override shared ones.
    # JX resolves the first matching template path.
    if app_components_dir and app_components_dir.exists():
        catalog.add_folder(str(app_components_dir), preload=True)
        catalog.add_folder(str(app_components_dir), prefix="ui", preload=True)

    # Shared components as fallback.
    catalog.add_folder(str(UI_COMPONENTS_DIR), preload=True)
    catalog.add_folder(str(UI_COMPONENTS_DIR), prefix="ui", preload=True)

    env = catalog.jinja_env
    env.filters["markdown"] = render_markdown
    env.globals.update(
        {
            "settings": settings,
            "env": settings.ENV,
            "is_production": settings.is_production,
            "is_development": settings.is_development,
            "PUBLIC_PORTFOLIO_URL": settings.PUBLIC_PORTFOLIO_URL,
            "PUBLIC_BLOG_URL": settings.PUBLIC_BLOG_URL,
            "PUBLIC_ADMIN_URL": settings.PUBLIC_ADMIN_URL,
        }
    )

    return catalog
