# Project Structure

Understanding how the files in this repository are organised is the first step to reading and changing the code with confidence.

---

## Directory Tree

```
tamagotchi/
│
├── src/                     # All application source code lives here
│   ├── __init__.py          # Makes src/ a Python package (empty, but required)
│   ├── app.py               # Application factory — creates the Flask app
│   ├── config.py            # Configuration classes (dev, testing, production)
│   ├── models.py            # SQLAlchemy database models (User, Pet)
│   ├── game.py              # Core Tamagotchi game logic (pure Python, no Flask)
│   │
│   ├── routes/              # Blueprint modules — each groups related endpoints
│   │   ├── __init__.py
│   │   ├── auth.py          # /api/auth/register  and  /api/auth/login
│   │   └── pets.py          # /api/pets  and all pet action endpoints
│   │
│   └── templates/           # Jinja2 HTML templates (server-rendered pages)
│       ├── base.html        # Shared layout (header, footer, navigation)
│       ├── home.html        # Landing page  GET /
│       ├── pets_list.html   # Pet list page  GET /api/pets  (HTML version)
│       └── pet_detail.html  # Single pet page  GET /api/pets/<id>  (HTML version)
│
├── tests/                   # Automated tests
│   ├── __init__.py
│   ├── conftest.py          # Shared pytest fixtures (app, client, db cleanup)
│   ├── test_game.py         # Unit tests for game.py logic
│   └── test_api.py          # Integration tests for every API endpoint
│
├── wsgi.py                  # Entry point — creates the app and runs the dev server
├── Procfile                 # Tells Render.com (and Heroku-style hosts) how to start the app
├── requirements.txt         # Python dependency list (pip install -r requirements.txt)
├── .gitignore               # Files that should never be committed to Git
├── instructions.txt         # Original project roadmap document
└── README.md                # High-level project overview
```

---

## Why This Layout?

### `src/` — source package

Putting all application code inside a `src/` directory (rather than the project root) keeps things tidy and avoids accidental imports of unrelated files. When Python imports `from src.models import db` it knows exactly where to look.

### Separation of concerns

Each file has one clear job:

| File | Responsibility |
|------|----------------|
| `app.py` | Wire everything together (create Flask app, register extensions and blueprints) |
| `config.py` | All settings in one place — no magic numbers scattered around the code |
| `models.py` | Define *what data* the app stores; no business logic here |
| `game.py` | Define *how the game works*; no Flask or database code here |
| `routes/auth.py` | Handle HTTP requests related to users |
| `routes/pets.py` | Handle HTTP requests related to pets |

Keeping game logic in `game.py` — separate from the Flask routes — means you can test it without a running web server (see [`testing.md`](testing.md)).

### `tests/` — mirror structure

The test directory mirrors the source structure. `test_game.py` tests `src/game.py`; `test_api.py` tests the routes. This makes it easy to find the relevant tests when editing any given file.

---

## The Request Lifecycle

Here is what happens when a browser or API client sends a request:

```
HTTP Request
     │
     ▼
 wsgi.py / gunicorn          ← receives the raw HTTP connection
     │
     ▼
 src/app.py  create_app()    ← Flask app object handles routing
     │
     ▼
 src/routes/pets.py          ← the matching Blueprint route function runs
     │         │
     │         ├──▶ src/game.py        ← business logic applied
     │         ├──▶ src/models.py      ← database read/write via SQLAlchemy
     │         └──▶ src/templates/     ← HTML rendered (if browser request)
     │
     ▼
HTTP Response (JSON or HTML)
```

---

## Key Python Concepts Illustrated Here

- **Package** — a directory containing an `__init__.py` file (`src/`, `src/routes/`, `tests/`)
- **Module** — a single `.py` file (`game.py`, `models.py`)
- **Import** — `from src.models import db` brings a name from one module into another
- **Application factory** — `create_app()` in `app.py` returns a configured Flask application object (explained fully in [`flask.md`](flask.md))
