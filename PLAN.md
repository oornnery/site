# Plano de Melhoria: Frontend + Backend

## Contexto

Site pessoal SSR com FastAPI + Jx/Jinja2. O codebase tem over-engineering na camada de services (classes wrapper desnecessarias), estrutura de pastas verbosa (infrastructure/, observability/, services/), templates com sintaxe Jinja verbosa (`{% if %}{% endif %}`, `{% for %}{% endfor %}`), e excesso de Tailwind inline nos componentes. O objetivo e simplificar tudo: estrutura flat funcional, componentes SolidJS-like, CSS semantico, API versionada, e avaliar minijinja.

---

## Fase 1: Reorganizacao Estrutural

### 1.1 Criar `app/routes/` e unificar views + API

**De:**
```
app/views/   (home, about, projects, blog, contact)
app/api/     (health, telemetry)
```

**Para:**
```
app/routes/
  __init__.py         # combina views_router + api_router
  views/
    __init__.py       # views_router com prefix /{lang}
    home.py, about.py, projects.py, blog.py, contact.py
  api/
    __init__.py       # api_router com prefix /api/v1
    health.py, telemetry.py
```

**Arquivos:** mover 7 route files, atualizar `app/main.py` (linhas 14-15, 120-122), atualizar imports em tests

### 1.2 Mover markdown pipeline para `app/content/`

- `app/infrastructure/markdown.py` -> `app/content/markdown.py`
- `app/infrastructure/gist.py` -> `app/content/gist.py` (se existir separado)
- Atualizar ~12 imports (services, deps, tests)

### 1.3 Mover notifications para `app/core/notifications.py`

- `app/infrastructure/notifications/email.py` -> `app/core/notifications.py` (flatten)
- Atualizar imports em `app/core/deps.py:12-17`, services
- Deletar `app/infrastructure/` (agora vazio)

### 1.4 Merge observability em `app/core/`

- `app/observability/telemetry.py` + `events.py` -> `app/core/telemetry.py` (~35 linhas)
- `app/observability/metrics.py` -> `app/core/metrics.py`
- Deletar `app/observability/`

**Resultado da Fase 1:**
```
app/
  main.py
  catalog.py
  routes/          # views + api
  models/          # inalterado por enquanto
  core/            # config, deps, rendering, security, i18n, language, logger, notifications, telemetry, metrics
  content/         # markdown pipeline
  templates/       # inalterado
```

---

## Fase 2: Eliminar Services Layer

### 2.1 Converter services simples em funcoes

| Service | Acao |
|---------|------|
| `HomePageService` (56 loc) | Converter para funcao `build_home_page()` em `routes/views/home.py` |
| `AboutPageService` (39 loc) | Converter para funcao `build_about_page()` em `routes/views/about.py` |
| `ProjectsPageService` (97 loc) | Converter para funcoes em `routes/views/projects.py` |
| `BlogPageService` (281 loc) | Converter para funcoes no topo de `routes/views/blog.py` |
| `ProfileService` (64 loc) | Converter para funcao `get_profile_globals()` em `app/core/profile.py` |

### 2.2 Mover SEO para core

- `app/services/seo.py` -> `app/core/seo.py` (ja sao funcoes, so mover)

### 2.3 Manter ContactOrchestrator simplificado

- Manter `ContactOrchestrator`, `ContactPageService`, `ContactSubmissionService`
- Mover para `app/core/contact.py` ou manter em `app/services/contact.py` (unico service restante)
- Simplificar telemetry recording repetitivo

### 2.4 Limpar `app/core/deps.py`

- Remover 6 factory functions (linhas 119-155 de deps.py)
- Manter: `get_catalog`, `limiter`, `render_template`, `get_contact_*`

### 2.5 Atualizar todos os testes

- Integration tests ja testam via routes (nao instanciam services diretamente)
- Atualizar imports, rodar `uv run task test_routes`

---

## Fase 3: Simplificar Models

### 3.1 Flatten context models

- `app/models/contexts/` (7 arquivos) -> `app/models/contexts.py` (arquivo unico)
- Todos os page contexts sao pequenos (5-10 campos), cabem em um arquivo

### 3.2 Criar `BasePageContext`

```python
class BasePageContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")
    seo: SEOMeta
    current_path: str = "/"
```

Todos herdam, reduz duplicacao de `model_config`.

### 3.3 Tipar `PageRenderData.context`

- De `context: Any` para `context: BasePageContext`

---

## Fase 4: Template Components + CSS Semantico

### 4.1 Criar componente `Show`

**Arquivo:** `app/templates/ui/control/show.jinja`
```jinja
{# def when=true #}
{% if when %}{{ content }}{% endif %}
```

**Uso:**
```jinja
<Show when={{ message }}>
    <Alert message={{ message }} tone="success" />
</Show>
```

### 4.2 Criar `ForEach` como Jinja2 Extension

Jx's `{{ content }}` slot e pre-renderizado - nao da pra passar variaveis de loop. Solucao: extensao Python.

**Arquivo:** `app/core/jinja_ext.py`
```python
class ForEachExtension(Extension):
    tags = {'foreach'}
    # Parse: {% foreach item in items %}...{% empty %}...{% endforeach %}
    # Compila para nodes.For (AST nativo do Jinja2)
```

**Registro:** em `get_catalog()` via `Catalog(extensions=[ForEachExtension])`

**Uso:**
```jinja
{% foreach post in posts %}
    <BlogCard post={{ post }} />
{% empty %}
    <Empty message="No posts found." />
{% endforeach %}
```

### 4.3 Criar `Switch/Case` como Jinja2 Extension

**Arquivo:** mesmo `app/core/jinja_ext.py`
```python
class SwitchExtension(Extension):
    tags = {'switch'}
    # Parse: {% switch expr %}{% case val1 %}...{% case val2 %}...{% default %}...{% endswitch %}
```

### 4.4 Extrair variantes para CSS semantico com @apply

**Arquivo novo:** `app/static/css/components.css`

```css
@layer components {
  /* Button */
  .btn { @apply inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200 focus:ring-4 focus:outline-none disabled:pointer-events-none disabled:opacity-50; }
  .btn-primary { @apply bg-accent text-background hover:bg-accent/85 shadow-sm shadow-accent/15 focus:ring-accent/30; }
  .btn-secondary { @apply bg-surface-2 text-foreground/80 border border-accent/15 hover:bg-surface-2/80; }
  .btn-ghost { @apply text-foreground/60 hover:bg-surface-2/50 hover:text-accent; }
  /* ... demais variantes */
  .btn-sm { @apply h-8 px-3 text-xs; }
  .btn-lg { @apply h-11 px-6 text-base; }

  /* Card, Tag, Alert, Input - mesmo padrao */
}
```

**Templates simplificados:**
```jinja
{# button.jinja - ANTES: 15 linhas de variant dicts #}
{# button.jinja - DEPOIS: #}
{% set cls = "btn btn-" ~ variant ~ " btn-" ~ size ~ (" w-full" if full_width else "") %}
```

**Componentes afetados:** `button.jinja`, `card.jinja`, `tag.jinja`, `alert.jinja`, `input.jinja`

### 4.5 Aplicar Show/ForEach nos templates existentes

Refatorar templates que usam `{% if %}` e `{% for %}` repetitivos:
- `features/blog/posts-fragment.jinja`
- `features/projects/list-fragment.jinja`
- `features/contact/form.jinja`
- `features/home/*.jinja`
- `features/resume/experience.jinja`

---

## Fase 5: API Versioning + minijinja + Polish

### 5.1 API com prefix `/api/v1`

- `api_router = APIRouter(prefix="/api/v1")`
- `/health` -> `/api/v1/health`
- `/otel/v1/traces` -> `/api/v1/telemetry/traces`
- Atualizar frontend telemetry JS endpoint
- Atualizar `_TRACING_SKIP_PATHS` em security.py
- Atualizar todos os tests

### 5.2 Avaliar minijinja-py (spike)

Criar benchmark script (nao vai para producao):
- Renderizar mesmo template com Jinja2 vs minijinja-py
- Medir tempo em 1000 iteracoes

**Bloqueio conhecido:** minijinja-py nao suporta Jinja2 extensions (ForEach/Switch). Jx depende do AST do Jinja2. Provavelmente inviavel sem reescrever Jx. Documentar resultado e fechar.

### 5.3 Decorator `@page_route` (opcional)

```python
def page_route(template: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            result = await func(request, *args, **kwargs)
            if isinstance(result, PageRenderData):
                return render_page(result, lang=get_lang(request))
            return result
        return wrapper
    return decorator
```

### 5.4 Atualizar documentacao

- `CLAUDE.md` - layer map, paths, architecture rules
- `docs/architecture.md`, `docs/backend.md`, `docs/frontend.md`

### 5.5 Otimizar skills

- Revisar 31 arquivos em `.agents/skills/` para redundancia
- Consolidar onde possivel

---

## Riscos

| Risco | Mitigacao |
|-------|-----------|
| Import breakage ao mover arquivos | `grep -r` antes de cada move; CI apos cada commit |
| ForEach extension conflitar com Jx parser | Jx so transforma tags TitleCase; `{% foreach %}` e transparente |
| CSS @apply quebrar build | Testar `uv run task build_css` apos cada mudanca |
| minijinja incompativel com Jx | Documentar e fechar; nao investir mais |
| Regressao de seguranca | Rodar `test_security` apos cada fase |

## Verificacao

Apos cada fase:
1. `uv run task ci` (fmt + lint + typecheck + test + md_check + jx_check)
2. `uv run task test_routes` (100% coverage gate)
3. `uv run task test_security`
4. Dev server manual: `uv run task run` e navegar todas as paginas

## Commits

Commits pequenos por tipo conforme guidelines do projeto:
- `refactor:` para moves e simplificacoes
- `feat:` para Show, ForEach, Switch, CSS components
- `test:` para atualizacoes de teste
- `docs:` para documentacao
