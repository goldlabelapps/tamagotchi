# Flask

Flask is a **micro web framework** for Python. "Micro" does not mean it is limited — it means Flask gives you a minimal core and lets you add only the pieces you need, rather than bundling everything upfront like a "batteries-included" framework would.

This project uses Flask 3, the current major version.

## Why Flask?

| Concern | Flask's answer |
|---------|---------------|
| Handle HTTP requests | Built-in routing system |
| Return HTTP responses | `jsonify()`, `render_template()`, `Response` |
| Organise code | Blueprints |
| Extend with databases, auth, etc. | Extensions (Flask-SQLAlchemy, Flask-JWT-Extended) |
| Render HTML | Jinja2 template engine (built-in) |

Flask alternatives include Django (more opinionated, larger, full-featured) and FastAPI (async, automatically generated docs). Flask is a great first framework because its source code is small enough to read and understand.

## How Flask is Used in this Project

### 1. The Application Factory (`src/app.py`)

```python
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from src.config import Config
from src.models import db
from src.routes.auth import auth_bp
from src.routes.pets import pets_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)   # load settings

    db.init_app(app)                        # initialise the database extension
    JWTManager(app)                         # initialise the JWT extension

    app.register_blueprint(auth_bp)         # register auth routes
    app.register_blueprint(pets_bp)         # register pet routes

    @app.route("/")
    def home():
        return render_template("home.html"), 200

    with app.app_context():
        db.create_all()                     # create tables if they don't exist

    return app
```

**Why a factory function?**

Instead of creating the Flask app as a module-level global, `create_app()` is a function that *returns* the app. This means:

- **Testing** — call `create_app(TestingConfig)` to get an app wired to an in-memory SQLite database without affecting production.
- **Multiple instances** — you can run multiple copies of the app in the same process (useful for testing).
- **Deferred initialisation** — extensions like SQLAlchemy are configured with the app inside the factory, avoiding circular imports.

### 2. Blueprints (`src/routes/auth.py`, `src/routes/pets.py`)

A Blueprint is a collection of routes (and other things) that can be registered on an application. Think of it as a mini-application that gets plugged in.

```python
# src/routes/auth.py
from flask import Blueprint, jsonify, request

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.post("/register")
def register():
    ...

@auth_bp.post("/login")
def login():
    ...
```

The `url_prefix="/api/auth"` means every route in this blueprint automatically starts with `/api/auth`. So `@auth_bp.post("/register")` handles requests to `POST /api/auth/register`.

**Benefits of Blueprints:**
- Related routes are grouped together in one file
- `url_prefix` keeps URL namespacing clean
- Blueprints can be registered (or not) depending on configuration

### 3. Routing

Flask maps URL patterns to Python functions using decorators:

```python
@pets_bp.get("")              # GET  /api/pets
def list_pets():
    ...

@pets_bp.get("/<int:pet_id>") # GET  /api/pets/42
def get_pet(pet_id: int):
    ...

@pets_bp.post("/<int:pet_id>/feed")  # POST /api/pets/42/feed
def feed_pet(pet_id: int):
    ...
```

`<int:pet_id>` is a URL **converter** — Flask automatically converts the path segment to a Python `int` and passes it as the function argument.

Common converters: `<string:name>`, `<int:id>`, `<float:value>`, `<path:subpath>`.

### 4. The Request Object

`flask.request` is a thread-local proxy that gives access to the current HTTP request:

```python
from flask import request

data = request.get_json(silent=True) or {}   # parse JSON body
name = data.get("name")                       # read a field
```

`silent=True` means Flask returns `None` instead of raising an error if the body is not valid JSON.

### 5. Responses

```python
from flask import jsonify, render_template

# JSON response with a 200 status code
return jsonify({"pets": pet_dicts}), 200

# HTML response using a Jinja2 template
return render_template("pets_list.html", pets=pet_dicts), 200

# Error response
return jsonify({"error": "pet not found"}), 404
```

Flask routes return a tuple of `(response_body, status_code)`. When you omit the status code Flask uses 200.

### 6. Content Negotiation

The pets routes return JSON *or* HTML depending on what the client asks for:

```python
best = request.accept_mimetypes.best_match(["application/json", "text/html"])
if best == "text/html":
    return render_template("pets_list.html", pets=pet_dicts), 200
return jsonify({"pets": pet_dicts}), 200
```

A browser sends `Accept: text/html` by default, so it gets a rendered page. An API client (e.g. `curl` or Python's `requests` library) typically sends `Accept: application/json` and gets JSON back.

### 7. The Application Context

Flask has a concept of an **application context** — a scope that makes the current app available to extensions. The `with app.app_context():` block in `create_app()` ensures the database can be accessed during setup:

```python
with app.app_context():
    db.create_all()   # needs to know which app's database to use
```

You will encounter `app_context` in tests too (`conftest.py`).

## Key Flask Concepts Summary

| Concept | Where in this project |
|---------|----------------------|
| Application factory | `src/app.py` `create_app()` |
| Blueprint | `src/routes/auth.py`, `src/routes/pets.py` |
| Route decorator | `@auth_bp.post("/register")` |
| URL converter | `/<int:pet_id>` |
| Request object | `request.get_json()`, `request.accept_mimetypes` |
| JSON response | `jsonify(...)` |
| HTML response | `render_template(...)` |
| Application context | `with app.app_context():` |

## Further Reading

- [Flask official documentation](https://flask.palletsprojects.com/)
- [Flask Blueprints tutorial](https://flask.palletsprojects.com/en/latest/blueprints/)
- [Flask application factory pattern](https://flask.palletsprojects.com/en/latest/patterns/appfactories/)
