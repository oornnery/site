from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from apps.packages.catalog import build_catalog
from apps.packages.api.router import register_not_found_handler
from apps.packages.api.router import router as pkgs_api_router
from .api.router import router as api_router
from .web.router import router as web_router

APP_DIR = Path(__file__).resolve().parent
COMPONENTS_DIR = APP_DIR / "components"
STATIC_DIR = APP_DIR / "static"


def create_app() -> FastAPI:
    debug = os.getenv("DEBUG", "false").lower() == "true"

    app = FastAPI(title="admin", debug=debug)

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    app.state.catalog = build_catalog(
        app_components_dir=COMPONENTS_DIR,
        debug=debug,
        site_name="admin",
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)

    app.include_router(api_router)
    app.include_router(web_router)
    app.include_router(pkgs_api_router)
    register_not_found_handler(
        app,
        title="Admin - Page not found",
        brand="Admin",
        home_route_name="admin.home",
    )

    return app


app = create_app()
