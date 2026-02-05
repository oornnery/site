# Portfolio

Personal portfolio app. Runs on port **8000**.

## Run

```bash
uv run uvicorn apps.portfolio.app:app --reload --port 8000
```

Or use `uv run task dev` to start all apps together.

## Routes

| Route              | Description              |
| ------------------ | ------------------------ |
| `GET /`            | Home page                |
| `GET /status`      | Service health dashboard |
| `GET /api/healthz` | Health check JSON        |

## Structure

```bash
portfolio/
├── app.py           # FastAPI factory
├── api/router.py    # REST endpoints
├── web/router.py    # HTML pages
├── components/      # App-specific JX templates
└── static/          # App-specific assets
```

Add new pages in `web/router.py` and new API endpoints in `api/router.py`. Override shared UI components by placing templates with the same path in `components/`.
