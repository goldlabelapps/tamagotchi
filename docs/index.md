# Tamagotchi APP° — Documentation

Welcome to the Tamagotchi APP° documentation. This project is a multi-tenant virtual-pet REST API built with Python and Flask. It is designed as a practical learning project that demonstrates the building blocks of a real production web application.

If you are new to Python web development, work through these documents in order. Each one covers a distinct concept used in this codebase, with enough background that you understand *why* each tool or pattern exists — not just how to use it.

## Table of Contents

| # | Document | What you'll learn |
|---|----------|-------------------|
| 1 | [Project Structure](project-structure.md) | How the repository is laid out and how every file fits together |
| 2 | [Python Basics for this Project](python-basics.md) | Virtual environments, packages, modules, and the tools you need before writing a line of code |
| 3 | [Flask](flask.md) | What Flask is, the application factory pattern, Blueprints, and routing |
| 4 | [Databases & SQLAlchemy](databases-sqlalchemy.md) | Relational databases, the ORM pattern, models, and relationships |
| 5 | [Authentication & JWT](authentication-jwt.md) | Password hashing, JSON Web Tokens, and protecting routes |
| 6 | [REST APIs](rest-api.md) | What a REST API is, HTTP verbs, JSON, and status codes |
| 7 | [Jinja2 Templates](templates-jinja2.md) | Server-side HTML rendering and the template engine |
| 8 | [Configuration & Environment Variables](configuration.md) | Config classes, `.env` files, and keeping secrets out of source control |
| 9 | [Testing with pytest](testing.md) | Unit tests, integration tests, fixtures, and the Flask test client |
| 10 | [Game Logic](game-logic.md) | How the Tamagotchi stat system and time decay work |
| 11 | [Deployment on Render.com](deployment-render.md) | Gunicorn, the Procfile, Postgres, and deploying to the cloud |
| 12 | [CI/CD with GitHub Actions](cicd.md) | Continuous integration, automated testing, and deployment pipelines |
| 13 | [API Reference](api-reference.md) | Complete endpoint reference with request/response examples |

## Quick-start Cheat Sheet

```bash
# 1. Clone
git clone https://github.com/goldlabelapps/tamagotchi.git
cd tamagotchi

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dev server
python wsgi.py
# → http://localhost:5555

# 5. Run tests
pytest tests/ -v
```

## Technology Map

```
Python 3.12
 └── Flask 3          — web framework
      ├── Flask-SQLAlchemy  — database ORM
      ├── Flask-JWT-Extended — authentication
      └── Jinja2            — HTML templating

SQLite (dev) / PostgreSQL (production)
gunicorn               — production WSGI server
pytest                 — test runner
Render.com             — cloud hosting platform
```
