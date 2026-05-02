
# Tamagotchi APP°

| # | Document | What you'll learn |
|---|----------|-------------------|
| 1 | [Project Structure](docs/project-structure.md) | How the repository is laid out and how every file fits together |
| 2 | [Python Basics for this Project](docs/python-basics.md) | Virtual environments, packages, modules, and the tools you need before writing a line of code |
| 3 | [Flask](docs/flask.md) | What Flask is, the application factory pattern, Blueprints, and routing |
| 4 | [Databases & SQLAlchemy](docs/databases-sqlalchemy.md) | Relational databases, the ORM pattern, models, and relationships |
| 5 | [Authentication & JWT](docs/authentication-jwt.md) | Password hashing, JSON Web Tokens, and protecting routes |
| 6 | [REST APIs](docs/rest-api.md) | What a REST API is, HTTP verbs, JSON, and status codes |
| 7 | [Jinja2 Templates](docs/templates-jinja2.md) | Server-side HTML rendering and the template engine |
| 8 | [Configuration & Environment Variables](docs/configuration.md) | Config classes, `.env` files, and keeping secrets out of source control |
| 9 | [Testing with pytest](docs/testing.md) | Unit tests, integration tests, fixtures, and the Flask test client |
| 10 | [Game Logic](docs/game-logic.md) | How the Tamagotchi stat system and time decay work |
| 11 | [Deployment on Render.com](docs/deployment-render.md) | Gunicorn, the Procfile, Postgres, and deploying to the cloud |
| 12 | [CI/CD with GitHub Actions](docs/cicd.md) | Continuous integration, automated testing, and deployment pipelines |
| 13 | [API Reference](docs/api-reference.md) | Complete endpoint reference with request/response examples |

## The Game

Tamagotchi APP° was a handheld digital pet created in the 1990s. The toy required users to care for a virtual pet by feeding it, cleaning up after it, playing games, and monitoring its health and happiness. Neglecting the pet would result in it becoming sick or even dying, while attentive care would help it grow and thrive.

## Features
- Multi-tenant support (multiple users, each with their own pets)
- Virtual pet lifecycle: feeding, playing, cleaning, health, happiness
- Time-based stat decay — neglect your pet and it will suffer!
- Persistent state using SQLite (local) or Postgres (production)
- JWT-authenticated REST API

## Tech Stack
- Python 3.12
- Flask + Flask-JWT-Extended
- SQLAlchemy ORM
- psycopg2 (Postgres) / SQLite (dev)
- pytest
- Render.com (deployment)

## Contributing
Contributions are welcome! Please open issues or submit pull requests for new features, bug fixes, or improvements.
_This README will be updated as the project evolves._

