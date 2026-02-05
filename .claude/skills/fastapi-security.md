---
name: fastapi-security
description: >
  Security patterns for FastAPI applications. Use this skill when implementing authentication
  (JWT, OAuth2), preventing XSS/CSRF/SQL injection, configuring security headers (CSP, HSTS),
  hashing passwords (bcrypt, argon2), rate limiting, file upload validation, or handling OWASP
  top 10 threats. Triggers include security, XSS, CSRF, SQL injection, authentication, JWT,
  OAuth2, password hashing, OWASP, CSP, HSTS, rate limiting, or file upload validation.
---

# FastAPI Security

Comprehensive security reference for FastAPI applications. Covers XSS prevention, CSRF, SQL injection, authentication, password hashing, security headers, rate limiting, file uploads, and OWASP top 10.

---

## 1. Security Headers Middleware

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://unpkg.com https://cdn.tailwindcss.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        return response
```

**Middleware order** (top = outermost):

1. CORS (must be first)
2. Security headers
3. Request logging
4. GZip compression (last)

---

## 2. CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # NEVER ["*"] with credentials
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    max_age=3600
)
```

---

## 3. XSS Prevention

### Jinja2 Autoescape

```python
from jinja2 import Environment, select_autoescape

env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(
        enabled_extensions=("html", "htm", "xml", "jinja"),
        default_for_string=True
    )
)
```

```jinja
{# SAFE — auto-escaped #}
<h1>{{ user.name }}</h1>

{# SAFE — only for pre-sanitized content #}
{{ sanitized_html|safe }}

{# DANGEROUS — never do this #}
{% autoescape false %}{{ user_input }}{% endautoescape %}
```

### Input Sanitization

```python
import bleach

class CommentCreate(BaseModel):
    content: str = Field(..., max_length=5000)

    @field_validator("content")
    @classmethod
    def sanitize(cls, v: str) -> str:
        return bleach.clean(v, tags=["p", "br", "strong", "em", "a"], strip=True)
```

---

## 4. CSRF Protection

```python
# API endpoints: Use JWT in Authorization header (immune to CSRF)
# Form endpoints: Use CSRF tokens

@app.post("/forms/contact")
async def contact(request: Request, csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf(request)
    form_data = await request.form()
    ...
```

```jinja
<form method="POST" action="/forms/contact">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    ...
</form>
```

---

## 5. SQL Injection Prevention

```python
# SAFE — SQLAlchemy parameterizes automatically
stmt = select(User).where(User.name.ilike(f"%{name}%"))
result = await db.execute(stmt)

# SAFE — raw SQL with parameters
stmt = text("SELECT * FROM users WHERE id = :user_id")
result = await db.execute(stmt, {"user_id": user_id})

# DANGEROUS — never concatenate
query = f"SELECT * FROM users WHERE name = '{name}'"  # SQL INJECTION!
```

---

## 6. Authentication (JWT)

```python
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

@app.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
```

### Password Hashing (Modern)

```python
# Option 1: passlib + bcrypt
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Option 2: pwdlib + argon2 (OWASP recommended)
from pwdlib import PasswordHash
password_hash = PasswordHash.recommended()
hashed = password_hash.hash("password")
is_valid = password_hash.verify("password", hashed)
```

---

## 7. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/public")
@limiter.limit("100/minute")
async def public_endpoint(request: Request):
    ...

@app.post("/api/analyze")
@limiter.limit("5/minute")
async def expensive_endpoint(request: Request):
    ...
```

---

## 8. File Upload Validation

```python
import magic

async def validate_image(file: UploadFile) -> UploadFile:
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 5MB)")
    mime = magic.from_buffer(content, mime=True)
    if mime not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail=f"Invalid type: {mime}")
    await file.seek(0)
    return file

@app.post("/upload")
async def upload(
    file: Annotated[UploadFile, File()],
    form: Annotated[FileUploadForm, Form()]
):
    validated = await validate_image(file)
    ...
```

**Pitfalls**: Validate file MIME via magic numbers, not Content-Type header. Always set file size limits. Never trust the filename.

---

## 9. OWASP Top 10 Checklist

| #   | Threat                        | Mitigation                                          |
| --- | ----------------------------- | --------------------------------------------------- |
| 1   | Broken Access Control         | Role-based deps, `require_admin`, per-resource auth |
| 2   | Cryptographic Failures        | `SecretStr`, bcrypt/argon2, HTTPS enforcement       |
| 3   | Injection                     | SQLAlchemy ORM, parameterized queries, Pydantic     |
| 4   | Insecure Design               | Input validation, rate limiting, least privilege    |
| 5   | Security Misconfiguration     | Security headers middleware, CSP, HSTS              |
| 6   | Vulnerable Components         | `pip-audit`, `safety check`, update regularly       |
| 7   | Auth Failures                 | JWT + refresh tokens, strong passwords, MFA         |
| 8   | Data Integrity Failures       | File upload validation (magic), signed JWTs         |
| 9   | Logging & Monitoring Failures | Correlation IDs, security event logging             |
| 10  | SSRF                          | URL whitelist, domain validation                    |

---

## 10. HTTPS Enforcement

```python
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

## Quick Reference

```txt
AUTH:     JWT (access 15min + refresh 7d), OAuth2PasswordBearer, bcrypt/argon2
XSS:     Jinja2 autoescape=True, bleach sanitize, CSP headers
CSRF:    Token-based for forms, JWT header for API (immune)
SQLI:    ORM only, parameterized text(), never concatenate
FILES:   Magic number validation, size limits, allowed MIME types
HEADERS: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
RATE:    slowapi per-endpoint, per-user, stricter for expensive ops
HTTPS:   HTTPSRedirectMiddleware in production
OWASP:   See checklist above
```
