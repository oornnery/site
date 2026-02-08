# Admin App (`apps/admin`)

Painel autenticado para gestao de conteudo e configuracoes, executando na porta `8002`.

## Escopo do App

- Autenticacao e sessao do admin.
- CRUD de posts e projetos.
- Edicao de profile/resume/settings.
- Moderacao de comentarios.
- Dashboard e analytics simplificado (pageviews).

## Estrutura

```text
apps/admin/
├── app.py
├── api/router.py
├── web/router.py
└── components/
```

## Rotas Web (SSR/HTMX)

| Metodo | Rota |
|---|---|
| GET | `/` |
| GET | `/login` |
| POST | `/login` |
| GET | `/logout` |
| GET | `/admin` |
| GET/POST | `/admin/blog/new` |
| GET/POST | `/admin/blog/{post_id}` |
| POST | `/admin/blog/{post_id}/delete` |
| GET/POST | `/admin/projects/new` |
| GET/POST | `/admin/projects/{project_id}` |
| POST | `/admin/projects/{project_id}/delete` |
| GET/POST | `/admin/profile` |
| GET | `/admin/comments` |
| POST | `/admin/comments/{comment_id}/delete` |
| POST | `/admin/comments/{comment_id}/restore` |
| GET/POST | `/admin/settings` |
| POST | `/admin/settings/sync-github` |
| GET | `/admin/analytics` |
| GET | `/events/admin.analytics` |
| GET | `/admin/partials/posts/table` |
| GET | `/admin/partials/projects/table` |
| GET | `/admin/partials/toast` |
| POST | `/admin/partials/editor/preview` |

## Rotas API (JSON)

| Metodo | Rota |
|---|---|
| POST | `/api/auth/login` |
| POST | `/api/auth/logout` |
| GET | `/api/auth/me` |
| GET | `/api/auth/github/start` |
| GET | `/api/auth/github/callback` |
| POST | `/api/posts` |
| PUT/PATCH | `/api/posts/{post_id}` |
| DELETE | `/api/posts/{post_id}` |
| POST | `/api/projects` |
| PUT/PATCH | `/api/projects/{project_id}` |
| DELETE | `/api/projects/{project_id}` |
| GET | `/api/analytics/pageviews` |
| GET | `/api/audit` |

## Checklist de Migracao (Plano + `portfolio-old`)

### Base e seguranca

- [x] App separado com auth por cookie JWT.
- [x] Rotas protegidas por dependencia admin.
- [x] Headers de seguranca compartilhados.
- [x] Auditoria de operacoes de CRUD.

### Auth

- [x] Login/logout por email/senha.
- [x] Endpoint `/api/auth/me`.
- [x] Fluxo GitHub OAuth em modo dev (atalho para seeded admin).
- [ ] Fluxo OAuth completo de producao (provider real end-to-end).

### CRUD de conteudo

- [x] CRUD completo de posts (web + API).
- [x] CRUD completo de projetos (web + API).
- [x] Moderacao de comentarios (delete/restore).
- [x] Edicao de profile com experiencia, educacao, certificados, skills e social links.
- [x] Upload de icone customizado em social links do profile.
- [x] Settings para home (background, quantidade de cards, modo featured/fallback).

### UX admin

- [x] Sidebar colapsavel.
- [x] Toasters de sucesso/erro apos salvar/editar/excluir.
- [x] Preview de editor (parcial HTMX).
- [x] Analytics SSR com stream SSE em `/events/admin.analytics`.

### Pendencias (gap para paridade final)

- [x] Pagina dedicada de auditoria no web (`/admin/audit`).
- [x] Gestao de arquivos como modulo dedicado (`/admin/files`, `/api/files/upload`).
- [x] Streams SSE de auditoria/jobs (`/sse/audit/stream`, `/sse/jobs/stream`).
- [ ] CSRF hardening especifico para mutacoes web (alem das validacoes atuais).
- [ ] Rate limits granulares por rota sensivel (auth, profile save, comments ops).

## Execucao

```bash
uv run --package admin -- uvicorn --app-dir . apps.admin.app:app --reload --port 8002 --host 0.0.0.0
```

Ou subir tudo:

```bash
uv run task dev
```

## Testes relevantes

```bash
uv run pytest tests/test_apps.py::test_admin_root_redirects_to_login_when_unauthenticated -q
uv run pytest tests/test_apps.py::test_admin_auth_login_and_me -q
uv run pytest tests/test_apps.py::test_admin_project_edit_page_renders -q
uv run pytest tests/test_apps.py::test_admin_blog_edit_page_renders -q
```

## Contratos com `apps/packages`

- Models compartilhados: `User`, `Post`, `Project`, `Profile`, `Comment`, `AuditLog`, `PageView`, `Settings`.
- Services compartilhados: `AuthService`, `BlogService`, `ProjectService`, `ProfileService`, `CommentService`, `AnalyticsService`.
- Security compartilhada: cookie auth, middlewares, helpers.
