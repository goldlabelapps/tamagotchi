# Databases & SQLAlchemy

Almost every web application needs to store data that persists beyond a single request. This project uses a **relational database** managed through **SQLAlchemy**, Python's most popular database toolkit.

---

## 1. Relational Databases in One Minute

A relational database stores data in **tables** (like spreadsheet sheets). Each row is a record; each column is a field.

```
users table
┌────┬──────────┬─────────────────────┬─────────────────────────┐
│ id │ username │ email               │ password_hash           │
├────┼──────────┼─────────────────────┼─────────────────────────┤
│  1 │ alice    │ alice@example.com   │ pbkdf2:sha256:...       │
│  2 │ bob      │ bob@example.com     │ pbkdf2:sha256:...       │
└────┴──────────┴─────────────────────┴─────────────────────────┘

pets table
┌────┬─────────┬──────────┬───────┬────────┬───────────┬──────────────┐
│ id │ user_id │ name     │ age   │ hunger │ happiness │ cleanliness  │
├────┼─────────┼──────────┼───────┼────────┼───────────┼──────────────┤
│  1 │       1 │ Pikachu  │     3 │   75.0 │      60.0 │         90.0 │
│  2 │       1 │ Buddy    │     1 │   40.0 │      80.0 │         55.0 │
│  3 │       2 │ Fluffy   │     0 │   50.0 │      50.0 │        100.0 │
└────┴─────────┴──────────┴───────┴────────┴───────────┴──────────────┘
```

The `user_id` column in `pets` is a **foreign key** — it references the `id` column in `users`. This creates the relationship: *a user has many pets*.

This project uses **SQLite** during development (a file-based database, no server needed) and **PostgreSQL** in production on Render.com.

---

## 2. What is an ORM?

Writing raw SQL is powerful but tedious and error-prone:

```sql
SELECT * FROM pets WHERE user_id = 1 AND id = 42;
```

An **ORM** (Object-Relational Mapper) lets you work with database rows as Python objects instead:

```python
pet = Pet.query.filter_by(user_id=1, id=42).first()
print(pet.name)   # "Pikachu"
```

SQLAlchemy is the standard ORM for Python. **Flask-SQLAlchemy** wraps it with Flask-friendly helpers.

---

## 3. The Models (`src/models.py`)

### Setting up SQLAlchemy

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()   # create the extension object (not yet attached to an app)
```

The `db` object is imported everywhere that needs database access. It gets attached to the Flask app inside `create_app()`:

```python
db.init_app(app)
```

### The `User` Model

```python
class User(db.Model):
    __tablename__ = "users"

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    pets = db.relationship("Pet", backref="owner", lazy=True, cascade="all, delete-orphan")
```

Each class attribute that is a `db.Column` maps to a column in the database table.

| Argument | Meaning |
|----------|---------|
| `db.Integer` / `db.String(80)` | Column data type |
| `primary_key=True` | This column uniquely identifies each row |
| `unique=True` | No two rows can have the same value |
| `nullable=False` | The column cannot be empty (`NOT NULL` in SQL) |
| `default=...` | Value used if none is provided at insert time |

### The `Pet` Model

```python
class Pet(db.Model):
    __tablename__ = "pets"

    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name         = db.Column(db.String(80), nullable=False)
    age          = db.Column(db.Integer, default=0)
    hunger       = db.Column(db.Float, default=50.0)
    happiness    = db.Column(db.Float, default=50.0)
    cleanliness  = db.Column(db.Float, default=100.0)
    health       = db.Column(db.Float, default=100.0)
    is_alive     = db.Column(db.Boolean, default=True)
    last_updated = db.Column(db.DateTime, ...)
    created_at   = db.Column(db.DateTime, ...)
```

`db.ForeignKey("users.id")` tells SQLAlchemy that `user_id` references the `id` column in the `users` table.

---

## 4. Relationships

The `db.relationship()` call on `User` tells SQLAlchemy how the two tables are connected:

```python
pets = db.relationship("Pet", backref="owner", lazy=True, cascade="all, delete-orphan")
```

| Argument | Effect |
|----------|--------|
| `"Pet"` | The related model class |
| `backref="owner"` | Adds `pet.owner` as a shortcut back to the user (auto-created) |
| `lazy=True` | Pets are only loaded from the database when you access `user.pets` |
| `cascade="all, delete-orphan"` | When a user is deleted, all their pets are automatically deleted too |

```python
# Using the relationship
user = User.query.get(1)
for pet in user.pets:       # SQLAlchemy fetches pets lazily here
    print(pet.name)

pet = Pet.query.get(42)
print(pet.owner.username)   # backref lets you navigate from pet → user
```

---

## 5. Creating Tables

`db.create_all()` reads all model classes and creates any tables that do not already exist:

```python
with app.app_context():
    db.create_all()
```

This is called every time the app starts (see `src/app.py`). It is safe to run repeatedly — it skips tables that already exist. For schema *changes* on an existing database you would need a migration tool like **Flask-Migrate** (Alembic). This project keeps things simple and just recreates tables in testing.

---

## 6. The Session — Reading and Writing Data

SQLAlchemy uses a **session** as a staging area for database changes. Changes are only saved to the database when you call `commit()`.

```python
# CREATE — add a new record
pet = Pet(user_id=user_id, name="Buddy")
db.session.add(pet)
db.session.commit()       # INSERT executed here

# READ — query existing records
pet = Pet.query.filter_by(id=pet_id, user_id=user_id).first()
pets = Pet.query.filter_by(user_id=user_id).all()

# UPDATE — modify an attribute, then commit
pet.hunger = 80.0
db.session.commit()       # UPDATE executed here

# DELETE — mark for deletion, then commit
db.session.delete(pet)
db.session.commit()       # DELETE executed here
```

In this project, `db.session.commit()` is called in each route handler *after* the game logic runs, to persist changes.

---

## 7. `to_dict()` — Serialising for JSON

SQLAlchemy model objects cannot be sent directly as JSON. Each model has a `to_dict()` method that converts it to a plain Python dictionary:

```python
def to_dict(self) -> dict:
    return {
        "id": self.id,
        "name": self.name,
        "hunger": round(self.hunger, 1),
        ...
    }
```

Flask's `jsonify()` then turns the dictionary into a JSON response.

---

## 8. SQLite vs PostgreSQL

| | SQLite | PostgreSQL |
|--|--------|-----------|
| Setup | Zero — it's a file | Requires a running server |
| Best for | Local development, testing | Production |
| Multi-user concurrent writes | Limited | Excellent |
| URL format | `sqlite:///tamagotchi.db` | `postgresql://user:pass@host/db` |

Render.com provides managed PostgreSQL. The `Config` class contains a small fix for a Render-specific URL format difference:

```python
if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
```

---

## Further Reading

- [SQLAlchemy documentation](https://docs.sqlalchemy.org/)
- [Flask-SQLAlchemy documentation](https://flask-sqlalchemy.palletsprojects.com/)
- [PostgreSQL tutorial](https://www.postgresqltutorial.com/)
