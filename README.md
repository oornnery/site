# Site

Monorepo with 3 independent web applications using Python, FastAPI, and a shared design system built on JX components.

## Tech Stack

| Layer               | Technology                                                      |
| ------------------- | --------------------------------------------------------------- |
| **Runtime**         | Python 3.13                                                     |
| **Framework**       | FastAPI + Uvicorn (ASGI)                                        |
| **Templates**       | Jinja2 + [JX](https://jx.scaletti.dev) (server-side components) |
| **Styling**         | Tailwind CSS (CDN)                                              |
| **Interactivity**   | HTMX + Alpine.js + Idiomorph                                    |
| **Real-time**       | Server-Sent Events (SSE)                                        |
| **Package Manager** | uv (workspace)                                                  |
| **Linting**         | Ruff                                                            |
| **Testing**         | Pytest                                                          |
| **Process Manager** | Honcho + Taskipy                                                |

## Apps

| App           | Port             | Description                  |
| ------------- | ---------------- | ---------------------------- |
| **Portfolio** | `localhost:8000` | Personal portfolio site      |
| **Blog**      | `localhost:8001` | Blog with posts and articles |
| **Admin**     | `localhost:8002` | Administration panel         |

Each app is an independent FastAPI project with its own `pyproject.toml`, but they share a design system via `apps/packages/`.

## Quick Start

```bash
# Install dependencies
uv sync

# Run all 3 apps in parallel (hot-reload)
uv run task dev

# Open in browser
# Portfolio → http://localhost:8000
# Blog     → http://localhost:8001
# Admin    → http://localhost:8002
```

## Commands

```bash
uv run task dev          # Start all 3 apps via honcho
uv run task fmt          # Format code (Ruff)
uv run task lint         # Run lint checks (Ruff)
uv run task lint-fix     # Lint with autofix
uv run task test         # Run tests with coverage
```

Run a single app:

```bash
uv run uvicorn apps.portfolio.app:app --reload --port 8000
uv run uvicorn apps.blog.app:app --reload --port 8001
uv run uvicorn apps.admin.app:app --reload --port 8002
```

## Architecture

```bash
site/
├── apps/
│   ├── portfolio/          # App: Portfolio (port 8000)
│   │   ├── app.py          #   create_app() factory
│   │   ├── api/router.py   #   REST endpoints (/api/*)
│   │   ├── web/router.py   #   HTML pages
│   │   ├── components/     #   App-specific JX templates (override @ui)
│   │   └── static/         #   Static assets
│   ├── blog/               # App: Blog (port 8001) — same structure
│   ├── admin/              # App: Admin (port 8002) — same structure
│   └── packages/           # Shared code
│       ├── catalog.py      #   JX catalog builder
│       ├── api/router.py   #   Shared routes (health, status, 404)
│       └── components/     #   Design system (@ui prefix)
│           ├── layouts/    #     Layout, Navbar, Footer, Content
│           ├── pages/      #     Home, Error, Health
│           ├── partials/   #     Breadcrumb, ThemeToggle, Toast, Health*
│           └── ui/         #     Badge, Button, Card, Modal, StatusDot
├── tests/                  # Test suite (pytest, parametrized across all 3 apps)
├── .claude/skills/         # JX skills for Claude Code
├── Procfile.dev            # Process definitions (honcho)
├── pyproject.toml          # Root config (workspace, tasks, deps)
└── CLAUDE.md               # Claude Code reference
```

### App Factory Pattern

Every app follows the same pattern in `app.py`:

```python
def create_app() -> FastAPI:
    app = FastAPI(title="app-name")
    app.mount("/static", StaticFiles(...))           # Static assets
    app.state.catalog = build_catalog(...)            # JX catalog
    app.add_middleware(GZipMiddleware, ...)            # Compression
    app.include_router(api_router)                    # /api/*
    app.include_router(web_router)                    # HTML pages
    app.include_router(pkgs_api_router)               # Shared routes
    register_not_found_handler(app, ...)              # Custom 404
    return app
```

### Component System (JX)

Components live in `apps/packages/components/` with the `@ui` prefix. Each app can override shared components by placing templates with the same path in its own `components/` directory.

```python
# Render a component from Python
catalog.render("@ui/pages/Home.jinja", title="My Title", brand="Blog")
```

```jinja
{# Import and use components inside templates #}
{#import "@ui/ui/Card.jinja" as Card #}
{#import "@ui/ui/Button.jinja" as Button #}

<Card title="Title">
  <Button variant="primary" href="/action">Click</Button>
</Card>
```

### Shared Routes

Defined in `apps/packages/api/router.py`, available to all apps:

| Route                               | Method | Description                                        |
| ----------------------------------- | ------ | -------------------------------------------------- |
| `/api/healthz`                      | GET    | Per-app health check (JSON)                        |
| `/healthz/summary`                  | GET    | Aggregated health across all 3 apps (HTMX partial) |
| `/healthz/logs/stream?service_id=X` | GET    | SSE stream with real healthz JSON per app          |
| `/status`                           | GET    | Status dashboard with live polling (10s)           |

## Design Patterns

### Frontend

- **HTMX**: Server-driven interactions without custom JavaScript. Server-rendered partials injected via `hx-get`/`hx-post`
- **Alpine.js**: Lightweight client-side state (dark mode, accordions, modals). Re-initialized after HTMX swaps via `htmx:afterSwap`
- **Idiomorph**: Morph swaps (`hx-swap="morph:innerHTML"`) for flicker-free updates on the health summary
- **SSE**: Alpine-managed EventSource with `connect()`/`disconnect()` lifecycle, automatic cleanup on `htmx:before-swap`
- **Toast OOB**: Notifications via `hx-swap-oob="true"` targeting `#toast-portal`
- **Dark Mode**: Toggle via Alpine `x-data` on `<body>`, persisted to `localStorage`, respects `prefers-color-scheme`

### Backend

- **Async**: All routes are `async`, `httpx.AsyncClient` for inter-service calls, `asyncio.gather` for concurrent health checks
- **App Factory**: `create_app()` pattern with catalog on `app.state`, clean separation of API and Web routers
- **Route Naming**: `name="app.home"` convention used by the 404 handler to generate navigation links
- **GZip**: Compression middleware enabled for all responses > 1000 bytes

### UI Components

| Component     | Type    | Description                                          |
| ------------- | ------- | ---------------------------------------------------- |
| `Layout`      | layout  | Base HTML with Tailwind, HTMX, Alpine, dark mode     |
| `Navbar`      | layout  | Sticky header with backdrop-blur, dynamic brand      |
| `Card`        | ui      | Container with title, subtitle, footer slot          |
| `Button`      | ui      | Renders `<a>` or `<button>`, 4 variants, 3 sizes     |
| `Modal`       | ui      | Alpine overlay with ESC, backdrop click, auto-remove |
| `Badge`       | ui      | Inline badge with tones (success, danger, neutral)   |
| `StatusDot`   | ui      | Green/red status indicator                           |
| `Toast`       | partial | Fixed top-right notification, auto-dismiss 3s        |
| `ThemeToggle` | partial | Sun/moon button for dark mode                        |
| `Breadcrumb`  | partial | Navigation with separators                           |

## TODO

### Portfolio (port 8000)

- [ ] "About" page with bio and photo
- [ ] Project list with cards
- [ ] Project detail page
- [ ] Skills/technologies section
- [ ] Social links and contact info
- [ ] Per-page SEO meta tags

### Blog (port 8001)

- [ ] Post model (title, slug, content, date, tags)
- [ ] Post list with pagination
- [ ] Individual post page
- [ ] Markdown rendering
- [ ] Tag filtering
- [ ] RSS/Atom feed

### Admin (port 8002)

- [ ] Authentication (login/logout)
- [ ] Blog post CRUD
- [ ] Content editor (Markdown)
- [ ] Image upload
- [ ] Dashboard with metrics
- [ ] Portfolio project management

### Infrastructure

- [ ] Database (SQLModel + aiosqlite or PostgreSQL)
- [ ] Migrations (Alembic)
- [ ] Environment variables (.env)
- [ ] Docker / docker-compose
- [ ] CI/CD (GitHub Actions)
- [ ] Deploy (VPS / Cloud)
- [ ] Domain and HTTPS
- [ ] Tailwind CSS build (move off CDN)

## Testing

```bash
# Run all tests
uv run task test

# Run a specific test
uv run pytest tests/test_apps.py::TestHomePage -v

# Run with detailed output
uv run pytest tests/ -v --tb=short
```

Tests use a parametrized `client` fixture that runs each test against all 3 apps automatically. Fixtures are defined in `tests/conftest.py`.
