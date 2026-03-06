---
trigger: always_on
---

# Python Backend Dependency and Version Rules

## Core Principle

When working on this repository, do not guess package APIs, dependency names, connection URL schemes, or version compatibility from memory.
For any framework or library integration, first verify the currently installed version and then write code that matches that version.

You must treat version-sensitive code as high risk.

---

## Mandatory Version-Check Workflow

Before changing code related to framework setup, ORM config, test setup, startup lifecycle, database connection, or model definitions, do the following in order:

1. Inspect the actual installed package versions from the project environment.
2. Check the project's dependency source of truth:
   - `pyproject.toml`
   - `requirements.txt`
   - `requirements-dev.txt`
   - `uv.lock`
   - `poetry.lock`
   - `pdm.lock`
3. If the environment and lock/config differ, trust the actual installed environment for immediate debugging, but note the mismatch explicitly.
4. Only after confirming versions may you propose code changes.

Do not assume examples from older tutorials apply.

---

## Version-Sensitive Libraries

Treat these as version-sensitive and verify before coding:

- FastAPI
- Starlette
- Pydantic
- Tortoise ORM
- asyncmy
- aiomysql
- pytest
- pytest-asyncio
- anyio
- httpx

---

## Tortoise ORM Rules

### 1. Never guess DB URL schemes

For Tortoise ORM, do not assume the database URL scheme from the driver name.

Specifically:
- Do not assume `asyncmy://` is a valid Tortoise DB URL scheme.
- Verify the scheme supported by the installed Tortoise version before editing config.
- Distinguish between:
  - the ORM's accepted URL scheme
  - the underlying driver package

If debugging a startup failure with `Unknown DB scheme`, inspect:
- Tortoise version
- current DB URL string
- whether the scheme belongs to Tortoise or only to the driver

### 2. Always check special characters in DB credentials

When a password contains special characters such as `@`, `:`, `/`, `?`, `#`, or `%`, do not paste it raw into a DB URL.
Check whether URL encoding is required.

### 3. Prefer project-local patterns over generic examples

If the repo already contains working Tortoise init code, test fixtures, or connection config, reuse that exact pattern unless there is a confirmed version-specific reason not to.

### 4. Watch for deprecated field arguments

When editing Tortoise models, verify whether the installed version expects:
- `primary_key` instead of `pk`
- `db_index` instead of `index`

Do not introduce deprecated arguments in new code.

### 5. Do not rewrite model APIs blindly

Before changing `fields`, `ForeignKeyField`, `ManyToManyField`, `pydantic_model_creator`, or FastAPI integration helpers, inspect existing working usage in the repo first.

---

## FastAPI / Starlette Rules

### 1. Always verify imports explicitly

Do not assume symbols are globally available.
If using `APIRouter`, `Depends`, `HTTPException`, `status`, or `Body`, verify they are imported in the file.

### 2. Treat startup/lifespan code as version-sensitive

When modifying app startup, shutdown, lifespan, or ORM registration:
- inspect the installed FastAPI and Starlette versions
- match the style already used in the repo
- avoid mixing older startup-event patterns and newer lifespan patterns unless verified

### 3. Test collection errors are import/config problems first

If pytest fails during collection:
- first inspect import errors
- then router/module structure
- then startup side effects
- do not jump straight to business logic fixes

---

## Test Debugging Rules

When a test fails, classify the failure before proposing a fix:

1. **Collection/import error**
   - missing import
   - circular import
   - module path issue
   - syntax error

2. **Startup/config error**
   - bad DB URL
   - ORM init failure
   - missing env var
   - lifespan failure

3. **Runtime logic error**
   - endpoint logic
   - validation
   - auth
   - query behavior

4. **Assertion mismatch**
   - response shape changed
   - expected status changed
   - fixture data mismatch

Do not treat all failures as business logic problems.

---

## Required Debugging Output Format

For dependency or framework-related failures, respond in this format:

### Root cause
State the exact failing layer:
- import
- startup
- config
- ORM init
- runtime
- assertion

### Evidence
Quote the exact traceback line that proves the diagnosis.

### Version check
List the relevant installed package versions involved.

### Fix
Give the minimal code or config change needed.

### Confidence
State whether this is:
- confirmed from traceback
- highly likely
- possible but needs environment confirmation

---

## Anti-Hallucination Rules

You must not:
- invent package APIs
- invent supported DB URL schemes
- infer compatibility from package names alone
- recommend migrations to new syntax unless version compatibility is confirmed
- mix examples from different major versions without warning

If uncertain, say exactly what must be checked.

---

## Repository-First Rule

When the repo already has one passing test or one working module using the same stack, prefer that implementation pattern over internet memory.

Priority order:
1. passing code already in this repo
2. installed package behavior in this environment
3. project dependency files
4. external examples

---

## Change-Minimization Rule

For version-related issues, prefer the smallest viable fix:
- fix import
- fix config string
- fix deprecated arg name
- align one function call to installed version

Do not refactor unrelated modules while debugging a version mismatch.

---

## If Unsure

If there is any uncertainty around versions, first inspect:
- installed packages
- dependency files
- working examples in the repo
- exact traceback

Only then propose a change.