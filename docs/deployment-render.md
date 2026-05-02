# Deployment on Render.com

Getting your app running locally is one thing. Making it available on the internet — reliably, securely, and without manual babysitting — is another. This document explains how this project is deployed to **Render.com** and introduces the production-specific pieces: `gunicorn`, the `Procfile`, PostgreSQL, and environment variables.

## 1. What is Render.com?

[Render.com](https://render.com) is a **Platform as a Service (PaaS)** — a cloud provider that handles the infrastructure (servers, networking, TLS certificates, scaling) so you can focus on the application.

You push code to GitHub; Render builds and deploys it automatically.

Render is a popular choice for Python/Flask apps because:
- Free tier for small web services and databases
- Native support for `requirements.txt`, `Procfile`, and environment variables
- Built-in PostgreSQL databases
- Automatic TLS (HTTPS) certificates
- Easy preview deployments from pull requests

Alternatives to Render include **Heroku** (very similar, older), **Railway**, **Fly.io**, and **AWS/GCP/Azure** (more complex but more powerful).

## 2. The Production Server: gunicorn

When you run `python wsgi.py` locally, Flask's built-in development server starts. It is fine for development but is explicitly **not suitable for production**:

- It handles only one request at a time
- It is not optimised for performance or stability
- It has no process management or crash recovery

**gunicorn** (Green Unicorn) is a production-grade WSGI server for Python. It:
- Spawns multiple worker processes to handle concurrent requests
- Manages worker crashes and restarts
- Interfaces with the operating system efficiently

```bash
# Start gunicorn with 4 worker processes
gunicorn --workers 4 wsgi:app
```

`wsgi:app` tells gunicorn to import the module `wsgi` and use the variable `app` from it:

```python
# wsgi.py
from src.app import create_app

app = create_app()   # ← gunicorn imports this
```

gunicorn is installed via `requirements.txt`:

```
gunicorn==22.0.0
```

## 3. The `Procfile`

Render (and Heroku-compatible platforms) look for a file named `Procfile` in the project root to know how to start the application:

```
web: gunicorn wsgi:app
```

- `web:` — declares this is the web process type (handles HTTP traffic)
- `gunicorn wsgi:app` — the command to run

Render reads the `Procfile` and uses this command as the start command for the web service. You can also set this manually in the Render dashboard, but having it in source control means the deployment command is always in sync with the code.

## 4. WSGI — What Does It Mean?

**WSGI** (Web Server Gateway Interface) is the Python standard that defines how a web server (gunicorn) communicates with a web application (Flask). Any WSGI-compatible server can run any WSGI-compatible application.

```
Internet
   │
   ▼
gunicorn (WSGI server)   ← receives raw HTTP, manages workers
   │
   ▼  WSGI interface (PEP 3333)
   │
   ▼
Flask app (WSGI application)   ← processes request, returns response
```

You do not need to understand the WSGI protocol itself; just know that `wsgi.py` is the file that gunicorn imports to get a WSGI-compatible application object.

## 5. Deploying to Render — Step by Step

1. **Push your code to GitHub** (Render connects to your repository).

2. **Create a PostgreSQL database** on Render:
   - Dashboard → *New* → *PostgreSQL*
   - Render provides a `DATABASE_URL` environment variable automatically

3. **Create a Web Service** on Render:
   - Dashboard → *New* → *Web Service*
   - Connect your GitHub repository
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt` (Render fills this in automatically)
   - **Start Command**: `gunicorn wsgi:app` (or leave blank if you have a Procfile)

4. **Set environment variables** in the Render dashboard under *Environment*:

   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | A long random string (never reuse the dev key) |
   | `JWT_SECRET_KEY` | Another long random string |
   | `DATABASE_URL` | Copied from your Render PostgreSQL database (auto-linked if you connect the services) |

5. **Deploy** — Render installs dependencies, starts gunicorn, and your app is live on a `*.onrender.com` URL.

## 6. Generating Secure Secret Keys

Never use the placeholder dev keys (`"dev-secret-key-change-in-production"`) in production. Generate random keys:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Run this twice — once for `SECRET_KEY` and once for `JWT_SECRET_KEY`.

## 7. SQLite vs PostgreSQL in Production

SQLite writes to a file on disk. On Render's free tier, the filesystem is **ephemeral** — it is reset on every deployment. You would lose all your data.

PostgreSQL on Render is a managed, persistent, network-accessible database. The connection URL is provided as an environment variable. The `Config` class handles the `postgres://` → `postgresql://` URL scheme difference automatically:

```python
if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
```

In local development you keep `sqlite:///tamagotchi.db` (the default when no `DATABASE_URL` is set).

## 8. What Happens on Each Deploy

1. Render detects a new commit on the connected branch.
2. Render clones the repository.
3. Render runs the **build command** (`pip install -r requirements.txt`).
4. Render starts the **web process** (`gunicorn wsgi:app`).
5. On startup, `create_app()` runs `db.create_all()` — any new database tables are created automatically.
6. Old processes are replaced with new ones (zero-downtime rolling deploy on paid plans).

## 9. Render Free Tier Limitations

| Limitation | Notes |
|------------|-------|
| **Spin-down** | Free web services spin down after 15 minutes of inactivity; the next request takes ~30 s to wake up |
| **PostgreSQL** | Free database expires after 90 days; paid plans are persistent |
| **Build minutes** | Limited per month on the free tier |

For a learning project or portfolio demo these limitations are fine. Production apps typically use a paid plan.

## 10. Logs and Debugging on Render

Render streams application logs in real time in the dashboard (*Logs* tab). `print()` statements and any unhandled exceptions appear there. For structured production logging, consider the Python `logging` module instead of `print`.

## Further Reading

- [Render documentation](https://render.com/docs)
- [gunicorn documentation](https://docs.gunicorn.org/)
- [PEP 3333 — Python Web Server Gateway Interface](https://peps.python.org/pep-3333/)
- [12-Factor App — Disposability](https://12factor.net/disposability)
