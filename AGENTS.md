# AGENTS.md

## Quick Start

```bash
uv run main.py          # dev server on port 18000 with reload
```

## Prerequisites

`server/secret.py` is **gitignored and required**. Create it before the app can start:

```python
API_KEY = "<your-api-key>"
```

The app will crash at import time with an `ImportError` if this file is missing.

## Architecture

FastAPI app. Entry point: `server/main:app`. The `main.py` at root just calls `uvicorn.run`.

| Directory | Purpose |
|---|---|
| `server/api/` | Route modules, each using `APIRouter()`. Must be mounted in `server/main.py`. |
| `server/schema/` | Pydantic models. Response schemas inherit `ResponseSchema[T]`; data shapes inherit `DataSchema` (both in `server/schema/base.py`). |
| `server/database/` | Peewee models (`models.py`), SQLite connection singleton (`connect.py`), table/view creation + seed data (`setup.py`). DB file: `datas/lilac.db`. |
| `server/utils/` | Shared utilities: `auth.py` (session-based, `get_current_user` dependency), `image.py` (webp conversion + DB registration), `file.py` (path constants via `folder` class), `agent.py` (external Agent API client), `cache.py` (in-memory cache with `enable` decorator). |
| `server/tasks/` | Background periodic tasks (~1h interval). Auto-discovered — add a new `.py` file and use the `@register("name")` decorator from `server/tasks/register.py`. |

## Key Conventions

### API routes

- Create a new `.py` in `server/api/`, define `router = APIRouter()`, then mount in `server/main.py` with `app.include_router(router, prefix="/api/...", tags=[...])`.
- The image route uses prefix `/image` (no `/api/`), all others use `/api/`.
- Request Pydantic models are defined inline in the API file; response schemas live in `server/schema/`.

### Responses

- Every route returns a **specific** `ResponseSchema[T]` subclass (e.g. `ShareResponse`, `ChatResponse`), never bare `ResponseSchema`.
- Success: `ShareResponse(success=True, data=ShareData(...))`.
- Error: `ShareResponse(success=False, code=400, message="...")` — always the same concrete subclass, never a different type.

### Images

- All uploaded images are converted to webp via `convert_to_webp()` in `server/utils/image.py`.
- Only the UUID stem filename is stored in the DB (no path, no extension).
- Served via `GET /image/<name>` (accepts with or without `.webp` suffix).
- Static assets (e.g. default avatar) live in `public/`.

### Auth

- `get_current_user` from `server/utils/auth.py` is a FastAPI `Depends` — inject it in routes that need auth. Returns `Optional[User]` (may be `None`).
- Passwords are SHA-256 hashed (`get_password_hash`). Sessions use a random 64-char hex token stored in the `users` table, with a 7-day expiry.
- Helper `get_avatar_url(user)` returns `/image/<name>` or `/image/avatar` as fallback.

### Database

- SQLite via Peewee. Schema is created at app startup (lifespan calls `setup_database()`). No migration system — model changes require manual DB updates or wiping `datas/lilac.db`.
- **Views** are defined as raw SQL in `server/database/setup.py`, not as Peewee migrations. Corresponding read-only models in `models.py` have `primary_key = False`.
- Prefer view models (e.g. `PublicLetterFlow`, `UserProfile`) for multi-table or aggregate queries.
- **Foreign keys**: Peewee FK fields use `column_name` explicitly in several models to match the raw SQL schema. Check `models.py` before renaming columns.
- Always wrap DB access in `with db.connection_context():` (see any API file for pattern).
- **ORM classes must explicitly define the primary key field** (e.g. `id = AutoField()`). Do not rely on Peewee's implicit `id`.
- **Every ORM model (table or view) must be documented** in `server/database/README.md` with its SQL `CREATE` statement and field descriptions. When adding or modifying a model, update both `models.py` and the README in the same directory.

### Background tasks

- Add a `.py` in `server/tasks/`, decorate the main function with `@register("name")` from `server/tasks/register.py`. It will be auto-discovered and run periodically (~1h with jitter).
- Tasks run via `asyncio.to_thread`, so they must be synchronous (no `async def`).

### Logging

- Use `log("module_name").info/error(...)` from `server/utils/logger.py`.

### Cache

- In-memory cache via `server/utils/cache.py` (singleton `cache`).
- Decorate with `@cache.enable(expire=3600, only_today=True)` and call `cache.init(default)` inside the function.
- **The `default` argument of `cache.init()` must be a mutable object** (e.g. `dict`, `list`, `Counter()`). `init` returns the same object reference — the caller is expected to populate it via in-place mutation, and the decorator persists that same object after the function returns. Passing an immutable object (e.g. `int`, `str`, `tuple`) means the caller cannot mutate it in place, so the cached value will always remain the initial default, defeating the cache entirely.

## Tooling

Editor is Zed, which auto-applies **ruff** (linter/formatter) and **basedpyright** (type checker). No test suite is configured. Python 3.12, managed with `uv`.
