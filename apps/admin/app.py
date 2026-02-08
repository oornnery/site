from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles

from apps.packages.api.router import register_not_found_handler
from apps.packages.api.router import router as shared_router
from apps.packages.catalog import build_catalog
from apps.packages.db import init_db
from apps.packages.db.seed import seed_db
from apps.packages.security import PageviewMiddleware, SecurityMiddleware
from .api.router import router as api_router
from .web.router import router as web_router

APP_DIR = Path(__file__).resolve().parent
COMPONENTS_DIR = APP_DIR / "components"
APP_STATIC_DIR = APP_DIR / "static"
SHARED_STATIC_DIR = Path(__file__).resolve().parents[1] / "packages" / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    await seed_db()
    yield


def create_app() -> FastAPI:
    debug = os.getenv("DEBUG", "false").lower() == "true"

    app = FastAPI(title="admin", debug=debug, lifespan=lifespan)

    static_dir = SHARED_STATIC_DIR if SHARED_STATIC_DIR.exists() else APP_STATIC_DIR
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.state.catalog = build_catalog(
        app_components_dir=COMPONENTS_DIR,
        debug=debug,
        site_name="admin",
    )

    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(SecurityMiddleware)
    app.add_middleware(PageviewMiddleware, app_name="admin")

    app.include_router(api_router)
    app.include_router(web_router)
    app.include_router(shared_router)

    register_not_found_handler(
        app,
        title="Admin - Page not found",
        brand="Admin",
        home_route_name="admin.root",
    )

    return app


app = create_app()
