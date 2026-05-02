
# Tamagotchi APP°

## Table of Contents

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

How does the look in code? 

```python
HUNGER_DECAY_PER_HOUR = 10.0      # pet gets hungrier over time
HAPPINESS_DECAY_PER_HOUR = 8.0    # pet gets sadder over time
CLEANLINESS_DECAY_PER_HOUR = 5.0  # pet gets dirtier over time

# Action effect amounts
FEED_HUNGER_GAIN = 30.0
FEED_HAPPINESS_GAIN = 5.0

PLAY_HAPPINESS_GAIN = 25.0
PLAY_HUNGER_COST = 10.0

CLEAN_CLEANLINESS_GAIN = 40.0

# Health thresholds — below these values health starts to drop
HUNGER_CRITICAL_THRESHOLD = 20.0
HAPPINESS_CRITICAL_THRESHOLD = 20.0
CLEANLINESS_CRITICAL_THRESHOLD = 20.0

HEALTH_DECAY_PER_POOR_STAT = 5.0  # health lost per hour for each stat below threshold
AGE_GAIN_PER_HOUR = 1             # age increases every hour (in game units)
```

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

## Project Structure

```
src/
  app.py        # Flask application factory
  config.py     # Configuration classes
  models.py     # SQLAlchemy models (User, Pet)
  game.py       # Core Tamagotchi APP° game logic
  routes/
    auth.py     # Register / login endpoints
    pets.py     # Pet CRUD and action endpoints
tests/
  conftest.py   # Pytest fixtures
  test_game.py  # Unit tests for game logic
  test_api.py   # Integration tests for API
wsgi.py         # WSGI entry point (gunicorn)
Procfile        # Render.com process definition
requirements.txt
```

## Local Setup

```bash
# Clone the repo
git clone https://github.com/goldlabelapps/tamagotchi.git
cd tamagotchi

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) configure environment variables
cp .env.example .env   # then edit .env with your values

# Run the development server
python wsgi.py
```

The API will be available at `http://localhost:5000`.

## Environment Variables

| Variable        | Default (dev)                  | Description                    |
|-----------------|--------------------------------|--------------------------------|
| `DATABASE_URL`  | `sqlite:///tamagotchi.db`      | SQLAlchemy database URL        |
| `SECRET_KEY`    | `dev-secret-key-…`             | Flask secret key               |
| `JWT_SECRET_KEY`| `jwt-dev-secret-…`             | JWT signing key                |

## API Reference

### Auth

| Method | Endpoint              | Body                                | Description       |
|--------|-----------------------|-------------------------------------|-------------------|
| POST   | `/api/auth/register`  | `{username, email, password}`       | Register new user |
| POST   | `/api/auth/login`     | `{username, password}`              | Log in            |

Both endpoints return `{ user, access_token }`.

### Pets  *(all require `Authorization: Bearer <token>` header)*

| Method | Endpoint                    | Body          | Description        |
|--------|-----------------------------|---------------|--------------------|
| POST   | `/api/pets`                 | `{name}`      | Create a new pet   |
| GET    | `/api/pets`                 | —             | List your pets     |
| GET    | `/api/pets/<id>`            | —             | Get pet status     |
| POST   | `/api/pets/<id>/feed`       | —             | Feed the pet       |
| POST   | `/api/pets/<id>/play`       | —             | Play with the pet  |
| POST   | `/api/pets/<id>/clean`      | —             | Clean the pet      |

### Pet Stats

Each pet has four stats, all in the range **0–100**:

| Stat          | Starts at | Decays by (per hour) | Description                  |
|---------------|-----------|----------------------|------------------------------|
| `hunger`      | 50        | 10                   | 100 = full, 0 = starving     |
| `happiness`   | 50        | 8                    | 100 = ecstatic, 0 = miserable|
| `cleanliness` | 100       | 5                    | 100 = spotless, 0 = filthy   |
| `health`      | 100       | varies               | 0 = dead                     |

Health decreases when any of the other stats drop below 20. If health reaches 0 the pet dies.

## Running Tests

```bash
pytest tests/ -v
```

## Deployment on Render.com

1. Create a new **Web Service** connected to this repository.
2. Set the **Start Command** to `gunicorn wsgi:app` (the `Procfile` handles this automatically).
3. Add a **Postgres** database from the Render dashboard.
4. Set the environment variables `DATABASE_URL`, `SECRET_KEY`, and `JWT_SECRET_KEY` in the Render service settings.
5. Deploy — Render will install dependencies from `requirements.txt` automatically.

## Future Enhancements
- Pet evolution and random events
- Notifications / reminders
- Leaderboards or achievements
- Web UI

## Contributing
Contributions are welcome! Please open issues or submit pull requests for new features, bug fixes, or improvements.
_This README will be updated as the project evolves._

