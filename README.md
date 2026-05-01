# Tamagotchi

Tamagotchi is a multi-tenant Python app that recreates the classic handheld digital pet experience via a REST API.

## Background

Tamagotchi was a handheld digital pet created in the 1990s. The toy required users to care for a virtual pet by feeding it, cleaning up after it, playing games, and monitoring its health and happiness. Neglecting the pet would result in it becoming sick or even dying, while attentive care would help it grow and thrive.

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
  game.py       # Core Tamagotchi game logic
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

---
_This README will be updated as the project evolves._

