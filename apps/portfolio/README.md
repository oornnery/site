# Portfolio App (`apps/portfolio`)

Site publico do portfolio (SSR-first) executando de forma independente na porta `8000`.

## Escopo do App

- Paginas publicas do portfolio: home, about, projects, resume e contact.
- APIs publicas de profile/projects/contact.
- Sem paginas de blog/admin embutidas.
- Rotas antigas do monolito (`/blog`, `/admin`, `/login`) permanecem fora de escopo aqui (404).

## Estrutura

```text
apps/portfolio/
├── app.py
├── api/router.py
├── web/router.py
└── components/
```

## Rotas Web (SSR/HTMX)

| Metodo | Rota |
|---|---|
| GET | `/` |
| GET | `/about` |
| GET | `/projects` |
| GET | `/projects/{slug}` |
| GET | `/resume` |
| GET | `/resume.pdf` |
| GET | `/contact` |
| GET | `/partials/projects/grid` |
| POST | `/partials/contact/form` |

## Rotas API (JSON)

| Metodo | Rota |
|---|---|
| GET | `/api/projects` |
| GET | `/api/projects/{slug}` |
| GET | `/api/profile` |
| POST | `/api/contact` |

## Checklist de Migracao (Plano + `portfolio-old`)

### Base e arquitetura

- [x] App independente via `create_app()`.
- [x] Catalogo JX com componentes compartilhados + overrides do app.
- [x] Integracao com `apps/packages` (db, services, security, content).
- [x] Rotas compartilhadas de status/health disponiveis (`/status`, `/healthz/*`, `/api/healthz`).

### Frontend e UX

- [x] Home com layout baseado no legado (`portfolio-old`) e ajustes aprovados.
- [x] Home sem cards de blog (decisao do plano).
- [x] Navbar publica sem acao de login.
- [x] Link para blog no navbar.
- [x] About com conteudo completo.
- [x] About resumido na home e versao completa em `/about`.
- [x] Fundo da home controlado por configuracao e limitado a hero section.
- [x] Secao de contato com icones sociais e fallback de icones.
- [x] Home exibindo 4 projetos (configuravel por settings).

### Backend funcional

- [x] Listagem e detalhe de projetos.
- [x] Profile publico via API.
- [x] Formulario de contato via HTMX com validacao e feedback.
- [x] `resume.pdf` com WeasyPrint (fallback quando nao instalado).

### Seguranca e qualidade

- [x] Security headers compartilhados.
- [x] Pagina 404 HTML e 404 JSON para `/api/*`.
- [x] Cobertura de testes para fluxos principais do portfolio.

### Pendencias (gap para paridade final)

- [ ] Rate limit especifico no endpoint `/api/contact` (hoje nao esta aplicado na rota).
- [x] Persistencia de mensagens de contato (registro no banco via `ContactMessageService`).
- [ ] SEO avancado por pagina (metatags especificas e sitemap/robots por app).

## Execucao

```bash
uv run --package portfolio -- uvicorn --app-dir . apps.portfolio.app:app --reload --port 8000 --host 0.0.0.0
```

Ou subir tudo:

```bash
uv run task dev
```

## Testes relevantes

```bash
uv run pytest tests/test_apps.py::test_portfolio_home_has_no_blog_cards -q
uv run pytest tests/test_apps.py::test_portfolio_contact_page_connect_renders_icons -q
```

## Contratos com `apps/packages`

- Usa modelos compartilhados: `Profile`, `Project`, `Settings`.
- Usa services compartilhados: `ProfileService`, `ProjectService`, `BlogService`.
- Usa middlewares compartilhados: seguranca + pageview.
