# Blog App (`apps/blog`)

Site publico do blog executando de forma independente na porta `8001`.

## Escopo do App

- Home do blog (`/`) separada da listagem completa (`/posts`).
- Conteudo de posts, tags, categorias, busca, RSS.
- Comentarios (guest e autenticado) e reacoes.
- Sem telas administrativas.

## Estrutura

```text
apps/blog/
├── app.py
├── api/router.py
├── web/router.py
└── components/
```

## Rotas Web (SSR/HTMX)

| Metodo | Rota |
|---|---|
| GET | `/` |
| GET | `/posts` |
| GET | `/posts/{slug}` |
| GET | `/tags/{slug}` |
| GET | `/categories/{slug}` |
| GET | `/search` |
| GET | `/feed.xml` |
| GET | `/partials/posts/list` |
| GET | `/partials/posts/search` |
| GET | `/partials/comments` |
| POST | `/partials/comments/new` |
| POST | `/partials/reactions` |

## Rotas API (JSON)

| Metodo | Rota |
|---|---|
| GET | `/api/posts` |
| GET | `/api/posts/{slug}` |
| GET | `/api/tags` |
| GET | `/api/categories` |
| POST | `/api/posts/{slug}/reactions` |
| GET | `/api/comments/{post_slug}` |
| POST | `/api/comments/{post_slug}` |

## Checklist de Migracao (Plano + `portfolio-old`)

### Base e arquitetura

- [x] App separado (sem dependencias de render do portfolio/admin).
- [x] Catalogo JX com componentes blog-specific.
- [x] Rotas de status/health compartilhadas disponiveis.

### Frontend e UX

- [x] Home propria do blog em `/` (nao reaproveita a pagina de posts).
- [x] Listagem completa em `/posts`.
- [x] Navbar com `Home`, `Posts`, `RSS` e `Portfolio`.
- [x] Link de RSS abrindo em nova aba.
- [x] Branding atualizado para "Blog" + "by Fabio Souza" (navbar e paginas do blog).
- [x] Cards de posts com `reading time`.

### Conteudo e interacao

- [x] Detail de post com markdown renderizado.
- [x] Comentarios guest + autenticado.
- [x] Reacoes por post.
- [x] Filtros por tag/categoria e busca.
- [x] RSS feed em `/feed.xml`.

### Integracao com admin

- [x] Conteudo exibido no blog vem dos dados geridos no admin.
- [x] Moderacao de comentarios no admin impacta listagem publica.

### Pendencias (gap para paridade final)

- [ ] Paginas dedicadas de Tag/Category com template proprio (hoje reutiliza listagem).
- [ ] Busca full-text avancada (hoje busca basica por service).
- [ ] Realtime SSE para comentarios/reacoes no frontend publico (hoje fluxo principal e HTMX pull).
- [ ] Sitemap/robots/version por app.

## Execucao

```bash
uv run --package blog -- uvicorn --app-dir . apps.blog.app:app --reload --port 8001 --host 0.0.0.0
```

Ou subir tudo:

```bash
uv run task dev
```

## Testes relevantes

```bash
uv run pytest tests/test_apps.py::test_blog_home_and_posts -q
uv run pytest tests/test_apps.py::test_blog_post_detail_and_comments_flow -q
uv run pytest tests/test_apps.py::test_blog_reactions_api -q
```

## Contratos com `apps/packages`

- Models compartilhados: `Post`, `Comment`, `Reaction`.
- Services compartilhados: `BlogService`, `CommentService`.
- Render markdown + RSS via `apps/packages/content`.
- Middlewares compartilhados de seguranca/pageview.
