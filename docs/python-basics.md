# Python Basics for this Project

This document covers the Python fundamentals you need before diving into the application code. Even if you have written Python scripts before, web-application Python introduces a few important concepts — virtual environments, packages, and dependency management — that are easy to overlook.

---

## 1. Python Versions

This project targets **Python 3.12**. Python 2 is end-of-life and is never used for new projects. Always check which version you have:

```bash
python --version   # or python3 --version on some systems
```

If you have multiple Python versions installed, use `python3` explicitly, or set up `pyenv` to manage versions.

---

## 2. Virtual Environments

### The problem

Python packages are installed globally by default. If Project A needs `Flask==2.3` and Project B needs `Flask==3.0`, a global install can only hold one version at a time. This causes breakage across projects.

### The solution: `venv`

A virtual environment is an isolated copy of Python with its own package store. Changes inside the environment never affect other projects or your system Python.

```bash
# Create a virtual environment called .venv in the current directory
python -m venv .venv

# Activate it (macOS / Linux)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate

# You will see (.venv) in your prompt — all pip commands now affect only this environment
(.venv) $

# Deactivate when done
deactivate
```

> **Rule of thumb**: Always activate your virtual environment before working on a project. Always add `.venv/` to `.gitignore` (this project already does).

---

## 3. `pip` and `requirements.txt`

`pip` is Python's package installer.

```bash
pip install flask          # install the latest Flask
pip install flask==3.0.3   # install a specific version
pip list                   # show installed packages
pip freeze                 # show installed packages in requirements format
```

### `requirements.txt`

This file pins the exact versions of every dependency so that anyone who clones the project gets the same packages:

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-JWT-Extended==4.6.0
...
```

Install everything in one command:

```bash
pip install -r requirements.txt
```

> Never commit your `.venv/` folder. The `requirements.txt` file is the contract; anyone can recreate the environment from it.

---

## 4. Packages and Modules

| Term | Meaning | Example in this project |
|------|---------|-------------------------|
| **Script** | A single `.py` file you run directly | `wsgi.py` |
| **Module** | A `.py` file that is *imported* by other code | `src/game.py` |
| **Package** | A directory with an `__init__.py` file | `src/`, `src/routes/`, `tests/` |

### Imports

```python
# Absolute import — always preferred
from src.models import db
from src.config import Config

# Import a whole module
import src.game as game_logic

# Built-in module
from datetime import datetime, timezone
```

Python searches for modules in this order:
1. The current package
2. Directories listed in `sys.path` (which includes the project root when you run `pytest` or `python wsgi.py`)

---

## 5. Type Hints

The codebase uses Python type hints (`->`, `: str`, `: float`) as documentation for function signatures:

```python
def _clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    ...
```

Type hints are optional at runtime — Python does not enforce them — but they make code easier to understand and enable IDE autocompletion and static analysis tools such as `mypy`.

---

## 6. Dictionaries and JSON

Python dictionaries (`dict`) map directly to JSON objects. This is why `to_dict()` methods appear on the model classes:

```python
def to_dict(self) -> dict:
    return {
        "id": self.id,
        "username": self.username,
        "email": self.email,
    }
```

Flask's `jsonify()` function converts a Python dict into an HTTP response with a JSON body.

---

## 7. Environment Variables

Environment variables are key-value pairs set in the operating system, *outside* the application code. They are used to keep secrets (database passwords, API keys) out of source control.

```bash
# Set an environment variable in the shell (Linux / macOS)
export SECRET_KEY="my-super-secret-value"

# Read it in Python
import os
value = os.environ.get("SECRET_KEY", "fallback-default")
```

The `python-dotenv` package (included in `requirements.txt`) loads a `.env` file automatically:

```
# .env  (never commit this file!)
SECRET_KEY=my-super-secret-value
DATABASE_URL=postgresql://user:pass@host/db
JWT_SECRET_KEY=another-secret
```

See [`configuration.md`](configuration.md) for how this project uses environment variables.

---

## 8. `if __name__ == "__main__"`

You will see this pattern in `wsgi.py`:

```python
if __name__ == "__main__":
    app.run(debug=True, port=5555)
```

When Python runs a file *directly* (`python wsgi.py`), the special variable `__name__` is set to `"__main__"`. When the file is *imported* by another module, `__name__` is set to the module's name instead. This guard means the dev server only starts when you run the file directly, not when `gunicorn` imports it.

---

## 9. Common Standard Library Modules Used Here

| Module | Used for |
|--------|----------|
| `os` | Reading environment variables (`os.environ.get`) |
| `datetime` | Timestamping pet updates, calculating time elapsed |
| `timedelta` | Expressing durations (e.g. JWT expires in 24 hours) |
| `timezone` | Making datetimes timezone-aware (`timezone.utc`) |

---

## Next Steps

- [Project Structure](project-structure.md) — see how these concepts apply to the folder layout
- [Flask](flask.md) — start exploring the web framework
