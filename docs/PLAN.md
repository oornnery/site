# Plano de Migracao Monolito -> 3 Apps Independentes (Portfolio, Blog, Admin)

## Resumo

Migrar o conteudo e funcionalidades de `portfolio-old/app` para o monorepo atual (`apps/portfolio`, `apps/blog`, `apps/admin`, `apps/packages`) mantendo UX SSR-first com JX + HTMX e o visual existente, com estas decisoes ja travadas:

- Dominio canonico: `fabiosouza.com`.
- Escopo: paridade quase total ja na primeira entrega.
- Auth admin: email/senha + GitHub OAuth.
- URLs antigas do monolito: sem compatibilidade, comportamento padrao 404.
- Analytics: simplificado para pageviews (sem fingerprinting completo no MVP).
- Comentarios: guest + autenticado.

## Mudancas Publicas (APIs/Interfaces/Tipos)

- Separacao definitiva por app com contratos independentes de Web (SSR/HTMX) e API (JSON).
- Padronizacao de interfaces compartilhadas em `apps/packages`:
  - `Settings` compartilhado com URLs publicas por app.
  - `build_catalog(app_components_dir, site_name, debug, ...)`.
  - `get_session()` e modelos SQLModel em pacote comum.
  - Dependencias de auth (`get_current_user`, `get_current_admin_user`).
- Rotas antigas monoliticas (`/blog*`, `/admin*`, `/login`) no portfolio nao serao preservadas.
- API REST passa a ser organizada por dominio funcional por app, mantendo `/api/*` local de cada app.

## Arquitetura Alvo

- `apps/portfolio`: site publico de portfolio (sem blog embutido).
- `apps/blog`: site publico de blog.
- `apps/admin`: painel autenticado para CRUD e moderacao.
- `apps/packages`: nucleo compartilhado.
- Banco compartilhado unico (SQLite em dev, PostgreSQL em producao), sem chamadas HTTP entre apps no MVP.
- Reverse proxy em producao por subdominio (Caddy/Nginx).

## Estrutura Tecnica Final (Pacotes Compartilhados)

- `apps/packages/config.py`: `BaseSettings` central com:
  - `ENV`, `SECRET_KEY`, `DATABASE_URL`.
  - `PUBLIC_PORTFOLIO_URL`, `PUBLIC_BLOG_URL`, `PUBLIC_ADMIN_URL`.
  - Flags de seguranca e rate limit.
- `apps/packages/db/`:
  - `engine.py`, `session.py`, `migrations/` (Alembic), `seed.py`.
- `apps/packages/domain/models/`:
  - `user.py`, `post.py`, `project.py`, `profile.py`, `comment.py`, `reaction.py`, `settings.py`, `pageview.py`, `audit_log.py`.
- `apps/packages/domain/schemas/`:
  - DTOs de entrada/saida por dominio.
- `apps/packages/services/`:
  - `auth_service.py`, `blog_service.py`, `project_service.py`, `profile_service.py`, `comment_service.py`, `analytics_service.py`.
- `apps/packages/security/`:
  - JWT cookie auth, headers/CSP, validacao de origem HTMX, rate limit.
- `apps/packages/content/`:
  - markdown render/sanitize, RSS, SEO.
- `apps/packages/web/`:
  - helpers HTML/partial, errors, form parsing.
- `apps/packages/components/`:
  - design system JX compartilhado + layouts + partials + features.

## Contrato de Rotas (Frontend + Backend)

### Rotas Compartilhadas (`apps/packages/api/router.py`)

| Metodo | Rota | Uso |
|---|---|---|
| GET | `/status` | pagina SSR de saude |
| GET | `/healthz/summary` | partial HTMX de resumo |
| GET | `/healthz/logs` | log textual por servico |
| GET | `/healthz/logs/stream` | stream SSE de health |
| GET | `/api/healthz` | health JSON por app |

### Portfolio App (`fabiosouza.com`, porta 8000)

#### Web SSR/HTMX

| Metodo | Rota | Componente | Observacao |
|---|---|---|---|
| GET | `/` | `Home.jinja` | sem cards de blog |
| GET | `/about` | `About.jinja` | |
| GET | `/projects` | `Projects.jinja` | filtros HTMX |
| GET | `/projects/{slug}` | `ProjectDetail.jinja` | |
| GET | `/resume` | `Resume.jinja` | |
| GET | `/resume.pdf` | download PDF | |
| GET | `/contact` | `Contact.jinja` | form SSR/HTMX |
| GET | `/partials/projects/grid` | `ProjectGrid.jinja` | paginacao/filtro |
| POST | `/partials/contact/form` | `ContactForm.jinja` | validacao + toast OOB |

#### API JSON

| Metodo | Endpoint | Descricao |
|---|---|---|
| GET | `/api/projects` | lista projetos publicados |
| GET | `/api/projects/{slug}` | detalhe |
| GET | `/api/profile` | perfil publico |
| POST | `/api/contact` | envio de mensagem (rate-limited) |

### Blog App (`blog.fabiosouza.com`, porta 8001)

#### Web SSR/HTMX

| Metodo | Rota | Componente | Observacao |
|---|---|---|---|
| GET | `/` | `BlogHome.jinja` | home do blog |
| GET | `/posts` | `PostList.jinja` | paginacao/filtros |
| GET | `/posts/{slug}` | `PostDetail.jinja` | conteudo + comentarios + reacoes |
| GET | `/tags/{slug}` | `TagDetail.jinja` | |
| GET | `/categories/{slug}` | `CategoryDetail.jinja` | |
| GET | `/search` | `Search.jinja` | live search |
| GET | `/feed.xml` | RSS | |
| GET | `/partials/posts/list` | `PostList.jinja` | HTMX |
| GET | `/partials/posts/search` | `PostSearch.jinja` | HTMX |
| GET | `/partials/comments` | `Comments.jinja` | |
| POST | `/partials/comments/new` | `Comments.jinja` | guest + auth |
| POST | `/partials/reactions` | `Reactions.jinja` | contador OOB |

#### API JSON

| Metodo | Endpoint | Descricao |
|---|---|---|
| GET | `/api/posts` | filtros por tag/category/q/page |
| GET | `/api/posts/{slug}` | detalhe |
| GET | `/api/tags` | lista tags |
| GET | `/api/categories` | lista categorias |
| POST | `/api/posts/{slug}/reactions` | adiciona reacao |
| GET | `/api/comments/{post_slug}` | lista comentarios |
| POST | `/api/comments/{post_slug}` | cria comentario |

### Admin App (`admin.fabiosouza.com`, porta 8002)

#### Web SSR/HTMX

| Metodo | Rota | Componente | Observacao |
|---|---|---|---|
| GET | `/` | redirect | `/admin` ou `/login` |
| GET | `/login` | `Login.jinja` | sem aparecer em navbar publica |
| GET | `/logout` | logout + limpeza cookie | |
| GET | `/admin` | `Dashboard.jinja` | |
| GET | `/admin/blog` | `BlogList.jinja` | |
| GET | `/admin/blog/new` | `BlogEdit.jinja` | |
| POST | `/admin/blog/new` | submit create | |
| GET | `/admin/blog/{id}` | `BlogEdit.jinja` | |
| POST | `/admin/blog/{id}` | submit update | |
| POST | `/admin/blog/{id}/delete` | delete | |
| GET | `/admin/projects` | `ProjectsList.jinja` | |
| GET | `/admin/projects/new` | `ProjectEdit.jinja` | |
| POST | `/admin/projects/new` | create | |
| GET | `/admin/projects/{id}` | `ProjectEdit.jinja` | |
| POST | `/admin/projects/{id}` | update | |
| POST | `/admin/projects/{id}/delete` | delete | |
| GET | `/admin/profile` | `Profile.jinja` | |
| POST | `/admin/profile` | save profile | |
| GET | `/admin/comments` | `CommentsList.jinja` | moderacao |
| POST | `/admin/comments/{id}/delete` | soft delete | |
| POST | `/admin/comments/{id}/restore` | restore | |
| GET | `/admin/settings` | `Settings.jinja` | |
| POST | `/admin/settings` | save settings | |
| GET | `/admin/analytics` | `Analytics.jinja` | pageviews simplificado |
| GET | `/admin/partials/posts/table` | partial HTMX | |
| GET | `/admin/partials/projects/table` | partial HTMX | |
| GET | `/admin/partials/toast` | partial OOB | |
| POST | `/admin/partials/editor/preview` | markdown preview | |

#### API JSON autenticada

| Metodo | Endpoint | Descricao |
|---|---|---|
| POST | `/api/auth/login` | login |
| POST | `/api/auth/logout` | logout |
| GET | `/api/auth/me` | usuario atual |
| GET | `/api/auth/github/start` | inicio OAuth |
| GET | `/api/auth/github/callback` | callback OAuth |
| POST | `/api/posts` | create post |
| PUT/PATCH | `/api/posts/{id}` | update post |
| DELETE | `/api/posts/{id}` | delete post |
| POST | `/api/projects` | create project |
| PUT/PATCH | `/api/projects/{id}` | update project |
| DELETE | `/api/projects/{id}` | delete project |
| GET | `/api/analytics/pageviews` | metricas pageview |
| GET | `/api/audit` | trilha de auditoria |

## Design e UI/UX (Preservando Layout Existente)

- Migrar tokens e motion do legado para o design system compartilhado:
  - `tokens.css`, `motion.css`, classes de animacao/hover.
- Manter linguagem visual existente de navbar, cards, grids e admin, com ajustes:
  - Portfolio navbar: remover acao de login.
  - Portfolio navbar: manter link para Blog (`https://blog.fabiosouza.com`) e opcao Portfolio.
  - Blog navbar: incluir link Portfolio (`https://fabiosouza.com`).
  - Admin layout: sidebar colapsavel com Alpine (e menu mobile).
- Componentizacao final:
  - Compartilhado em `apps/packages/components`.
  - Overrides por app em `apps/<app>/components` quando necessario.
- Paginas de portfolio nao exibem cards de blog na home.

## Seguranca e Middleware

- Reaproveitar padroes do legado em `apps/packages/security`:
  - Security headers + CSP ambiente dev/prod.
  - Validacao de origem HTMX para requests mutaveis.
  - Rate limit especifico para auth/contact/comments.
  - JWT em cookie `HttpOnly`, `SameSite=Lax`, `Secure` em producao.
  - Cookie de admin host-only em `admin.fabiosouza.com`.
- Erros:
  - JSON padronizado para `/api/*`.
  - HTML 404/500 SSR para rotas web.

## Banco e Migracao de Dominio

- Consolidar modelos SQLModel do legado em pacote compartilhado.
- Ajustes de schema para separar responsabilidades por app mantendo DB unico.
- Alembic inicial com baseline completa.
- Seed minimo:
  - usuario admin,
  - profile inicial,
  - poucos posts/projetos de exemplo.
- Conteudo markdown:
  - salvar `content_md`,
  - gerar/sanitizar HTML para leitura rapida (`content_html`) quando aplicavel.

## Plano de Implementacao por Fases (Execucao)

### Fase 1: Foundation compartilhada

- Criar `config`, `db`, `security`, `content`, `web`, `services` em `apps/packages`.
- Conectar os 3 apps ao mesmo core compartilhado.
- Garantir `create_app()` com middleware e handlers consistentes.

### Fase 2: Design system e layouts

- Migrar componentes base do legado (`Base/Public/Admin`, `Navbar`, `Footer`, `Toast`, `Modal`, etc).
- Implementar admin sidebar colapsavel.
- Aplicar overlay de componentes por app no catalogo JX.

### Fase 3: Portfolio completo

- Migrar paginas SSR do portfolio.
- Remover cards de blog da home.
- Ajustar navbar sem login.
- Implementar APIs de profile/projects/contact.

### Fase 4: Blog completo

- Migrar list/detail/search/tags/categories/feed.
- Implementar partials HTMX (lista, busca, comentarios, reacoes).
- Comentarios guest+auth com moderacao.

### Fase 5: Admin completo

- Migrar login/logout/OAuth + protecao de rotas.
- CRUD posts/projetos/profile/settings/comments.
- Dashboard de pageviews simplificado.
- Toasters OOB e preview markdown.

### Fase 6: Shared health/status + observabilidade

- Consolidar `/status`, `/healthz/summary`, `/healthz/logs`, SSE health.
- Logging estruturado + request-id + auditoria admin.

### Fase 7: Documentacao detalhada

- Reescrever `apps/portfolio/README.md`.
- Reescrever `apps/blog/README.md`.
- Reescrever `apps/admin/README.md`.
- Atualizar `README.md` raiz com arquitetura e execucao local por subdominio.

## Plano de README por app (detalhado)

Cada README tera:

- Objetivo do app e fronteiras de responsabilidade.
- Arquitetura interna (`app/api/web/components/static`).
- Tabela completa de rotas Web e API.
- Dependencias e variaveis de ambiente.
- Fluxos principais (ex.: auth, CRUD, comentarios).
- Estrategia de testes do app.
- Checklist operacional (run, lint, test, debug).
- Limites e contratos com `apps/packages`.

## Testes e Cenarios de Aceite

### Testes backend

- Smoke por app: `/`, `/status`, `/api/healthz`.
- Contratos API por app com schemas e status codes.
- Auth admin:
  - login email/senha ok/erro,
  - OAuth callback,
  - rota protegida sem auth.
- Comentarios:
  - guest cria comentario,
  - usuario autenticado cria comentario,
  - moderacao admin delete/restore.
- Reacoes:
  - incremento e leitura de contagem.
- Portfolio:
  - home sem secao de posts/blog cards.
- Security:
  - headers presentes,
  - HTMX origin invalida bloqueada em mutacoes.
- 404:
  - rotas antigas no portfolio retornam 404.

### Testes frontend SSR/HTMX

- Render de paginas principais por app.
- Fluxos HTMX:
  - filtros/paginacao,
  - submit forms com erros e sucesso,
  - toast OOB.
- Navbar:
  - portfolio sem login,
  - links cruzados portfolio/blog funcionando.
- Admin sidebar:
  - estado colapsado/expandido em desktop e mobile.

### Criterios de aceite final

- 3 apps sobem independentes e funcionam juntos com `uv run task dev`.
- Portfolio, Blog e Admin operam em dominios separados no proxy.
- Sem dependencia HTTP entre apps para features core.
- UX visual preservada (tokens/motion/componentes) com ajustes solicitados.
- READMEs dos 3 apps completos e consistentes com implementacao.

## Assumptions e Defaults

- Dominio canonico de documentacao e config: `fabiosouza.com`.
- Sem redirecionamento/compatibilidade de rotas antigas do monolito.
- Analytics MVP focado em pageview e metricas essenciais.
- DB unico compartilhado entre apps.
- JWT cookie de admin isolado por host (`admin.fabiosouza.com`).
- Estrategia SSR-first com JX + HTMX + Alpine mantida.

## Implementacao Frontend Baseada no `portfolio-old`

- Toda pagina/partial do frontend deve sempre usar o `portfolio-old` como referencia direta de UI/UX.
- A implementacao no monorepo deve ficar igual ao legado no visual e comportamento, aplicando apenas os novos padroes e recomendacoes definidos (JX SSR, organizacao por app/packages, seguranca, qualidade e convencoes atuais).
- Excecoes permitidas somente para as mudancas ja aprovadas no plano (ex.: portfolio sem cards de blog na home, navbar publica sem login, separacao entre sites).
