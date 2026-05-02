# Configuration & Environment Variables

A well-structured application separates its *code* (logic) from its *configuration* (settings that change between environments). This project does that with a `Config` class and environment variables.

## 1. The Problem

Consider a database URL. In development you might use:

```
sqlite:///tamagotchi.db
```

In production (Render.com) you use:

```
postgresql://user:password@host:5432/tamagotchi
```

You do not want to hard-code the production URL into the source code because:
- It changes between environments
- It often contains credentials (passwords) that must never appear in version control

## 2. Environment Variables

An environment variable is a key-value pair that lives in the *operating system* outside your application. Programs read them at runtime using `os.environ`.

```bash
# Set in the shell (Linux / macOS)
export DATABASE_URL="postgresql://alice:secret@db.host/tamagotchi"
export SECRET_KEY="my-production-secret"
export JWT_SECRET_KEY="another-production-secret"

# Read in Python
import os
db_url = os.environ.get("DATABASE_URL")          # returns the value or None
db_url = os.environ.get("DATABASE_URL", "default") # returns "default" if not set
```

On Render.com (and most cloud platforms) you set environment variables in the dashboard, never in source code.

## 3. The `.env` File and `python-dotenv`

Typing `export VAR=value` in your terminal every time you open a new shell is tedious. The **`python-dotenv`** library reads a `.env` file and loads its contents into the environment automatically.

Create a `.env` file in the project root:

```
# .env  — NEVER commit this file to Git
SECRET_KEY=dev-only-secret
JWT_SECRET_KEY=dev-only-jwt-secret
DATABASE_URL=sqlite:///tamagotchi.db
```

Flask (via `python-dotenv`) picks this file up automatically when present. The `.gitignore` already excludes `.env` files:

```
.env
.env.*
```

> **Rule**: `.env` is for local development only. Production secrets go in the cloud provider's dashboard.

## 4. The `Config` Class (`src/config.py`)

```python
import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///tamagotchi.db"
    )
    # Render.com provides DATABASE_URL as postgres:// but SQLAlchemy needs postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-dev-secret-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)
```

### Why a class?

Using a Python class for configuration means:

- **Inheritance** — `TestingConfig` inherits all settings from `Config` and only overrides what differs.
- **No magic strings scattered in code** — every setting is defined in one file.
- **IDE support** — type checkers and editors understand class attributes.

### Loading the config

In `src/app.py`:

```python
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    ...
```

`app.config.from_object(Config)` reads all uppercase class attributes and loads them into Flask's config dictionary. In tests, `create_app(TestingConfig)` is used instead.

## 5. Config Reference

| Variable | Default (dev) | Description |
|----------|---------------|-------------|
| `SECRET_KEY` | `"dev-secret-key-…"` | Flask uses this to sign session cookies and other cryptographic operations |
| `DATABASE_URL` | `"sqlite:///tamagotchi.db"` | SQLAlchemy database connection string |
| `JWT_SECRET_KEY` | `"jwt-dev-secret-…"` | Key used to sign JWT tokens |
| `JWT_ACCESS_TOKEN_EXPIRES` | `timedelta(hours=24)` | How long an access token is valid |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` | Disables a deprecated SQLAlchemy feature that would generate unnecessary warnings |
| `TESTING` | `False` (not set) | Enables Flask test mode (better error propagation) |

## 6. The Render.com URL Fix

Render.com (and Heroku) provide the PostgreSQL connection URL with the scheme `postgres://`. SQLAlchemy requires `postgresql://`. The one-liner fix in `Config`:

```python
if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
```

The `1` at the end of `.replace()` means *replace only the first occurrence*, which is the correct and safe behaviour.

## 7. Testing Configuration

```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)
```

- `TESTING = True` — Flask propagates exceptions instead of returning 500 responses, giving clearer test failures.
- `"sqlite:///:memory:"` — the database lives in RAM and is destroyed after each test run, so tests never affect each other or production data.
- Short token expiry — makes it practical to test token expiration without waiting 24 hours.

## 8. What *Not* to Put in Environment Variables

Environment variables are great for secrets and settings that change per environment. They are not a good fit for:

- Large structured data (use a config file)
- Data that changes at runtime (use a database)
- Non-secret constants that are the same everywhere (just hard-code them)

## Further Reading

- [12-Factor App — Config](https://12factor.net/config) — industry standard guide on config management
- [python-dotenv documentation](https://github.com/theskumar/python-dotenv)
- [Flask configuration documentation](https://flask.palletsprojects.com/en/latest/config/)
