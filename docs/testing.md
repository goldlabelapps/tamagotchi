# Testing with pytest

Automated tests prove that your code works correctly — and keep working correctly as you change it. This project uses **pytest**, the most popular Python testing framework.

---

## 1. Why Write Tests?

- **Confidence** — you can refactor or extend code without fear of silently breaking existing behaviour.
- **Documentation** — tests show how functions are *supposed* to be called and what they return.
- **Fast feedback** — a test suite catches bugs in seconds, rather than discovering them in production.
- **CI/CD integration** — automated tests can run on every pull request (see [`cicd.md`](cicd.md)).

---

## 2. pytest Basics

pytest discovers and runs tests automatically. By convention:

- Test files are named `test_*.py` or `*_test.py`.
- Test functions are named `test_*`.
- Test classes are named `Test*`.

```bash
# Run all tests
pytest tests/ -v

# Run a specific file
pytest tests/test_game.py -v

# Run a specific test
pytest tests/test_game.py::TestFeed::test_feed_increases_hunger -v
```

A test passes if it completes without raising an exception. Use `assert` to check conditions:

```python
def test_addition():
    result = 1 + 1
    assert result == 2   # passes

def test_subtraction():
    result = 5 - 3
    assert result == 10  # fails — pytest shows a diff
```

---

## 3. Test Structure in this Project

```
tests/
  conftest.py    ← shared fixtures (setup code reused by many tests)
  test_game.py   ← unit tests for src/game.py
  test_api.py    ← integration tests for the HTTP endpoints
```

### Unit tests vs Integration tests

| | Unit Tests | Integration Tests |
|--|-----------|-----------------|
| What they test | A single function or class in isolation | Multiple components working together |
| Dependencies | Mocked/faked | Real (database, HTTP stack) |
| Speed | Very fast | Slower |
| File | `test_game.py` | `test_api.py` |

---

## 4. Fixtures (`tests/conftest.py`)

A **fixture** is a function decorated with `@pytest.fixture` that sets up (and optionally tears down) resources for tests. pytest injects fixtures automatically by matching parameter names.

```python
import pytest
from src.app import create_app
from src.config import TestingConfig
from src.models import db as _db


@pytest.fixture(scope="session")
def app():
    """Create the Flask app once for the entire test session."""
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app          # ← tests run here
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Return a Flask test client for one test function."""
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    """Wipe all DB rows after each test so tests don't affect each other."""
    with app.app_context():
        yield
        _db.session.remove()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
```

### Fixture scopes

| Scope | The fixture runs… |
|-------|------------------|
| `"session"` | Once for the entire test run |
| `"module"` | Once per test file |
| `"function"` | Once per test function (default) |

The `app` fixture has `scope="session"` because creating the Flask app and setting up the database is expensive — we only need to do it once. The `client` and `clean_db` fixtures have `scope="function"` so each test gets a fresh HTTP client and a clean database.

### `autouse=True`

`clean_db` has `autouse=True`, meaning pytest runs it automatically for every test function without needing to declare it as a parameter. This ensures no test can accidentally pollute another test's database state.

---

## 5. Unit Tests: Mocking (`tests/test_game.py`)

The game logic in `src/game.py` takes a `pet` object as an argument. In unit tests, instead of creating a real database-backed `Pet`, we use `unittest.mock.MagicMock`:

```python
from unittest.mock import MagicMock

def make_pet(name="Buddy", hunger=50.0, happiness=50.0, cleanliness=100.0,
             health=100.0, is_alive=True):
    pet = MagicMock()
    pet.name = name
    pet.hunger = hunger
    pet.happiness = happiness
    pet.cleanliness = cleanliness
    pet.health = health
    pet.is_alive = is_alive
    pet.age = 0
    pet.last_updated = datetime.now(timezone.utc)
    return pet
```

`MagicMock` creates a fake object that accepts attribute assignments (`pet.hunger = 80.0`) and method calls. This lets us test `game.py` logic entirely in memory — no Flask app, no database.

### Sample unit test

```python
class TestFeed:
    def test_feed_increases_hunger(self):
        pet = make_pet(hunger=40.0)
        result = feed(pet)
        assert result["success"] is True
        assert pet.hunger == pytest.approx(40.0 + FEED_HUNGER_GAIN, abs=0.5)
```

`pytest.approx` handles floating-point comparisons gracefully — instead of checking for exact equality (which can fail due to floating-point rounding), it checks that two numbers are approximately equal within a given tolerance.

---

## 6. Integration Tests: The Flask Test Client (`tests/test_api.py`)

The Flask test client simulates HTTP requests without running an actual HTTP server. Tests make requests and assert on the response status code and body.

```python
class TestPets:
    def _setup(self, client):
        register_user(client)
        token = login_user(client).get_json()["access_token"]
        return token

    def test_feed_pet(self, client):
        token = self._setup(client)
        # Create a pet
        pet = client.post(
            "/api/pets",
            data=json.dumps({"name": "Buddy"}),
            content_type="application/json",
            headers={"Authorization": f"Bearer {token}"},
        ).get_json()["pet"]

        initial_hunger = pet["hunger"]

        # Feed the pet
        resp = client.post(f"/api/pets/{pet['id']}/feed",
                           headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.get_json()["pet"]["hunger"] > initial_hunger
```

The `client` fixture is injected automatically because the test method parameter is named `client` — pytest finds the matching fixture in `conftest.py`.

---

## 7. Test Classes

This project organises tests into classes (`TestAuthRegister`, `TestPets`, etc.) for grouping — related tests live together and share helper methods like `_setup`. Using classes is optional; pytest works equally well with plain functions.

---

## 8. What is Tested

| Test | Coverage |
|------|----------|
| `TestApplyTimeDecay` | Stat decay, clamping, pet death, age increase |
| `TestFeed` | Hunger gain, happiness gain, clamping, dead pet |
| `TestPlay` | Happiness gain, hunger cost, dead pet |
| `TestClean` | Cleanliness gain, dead pet |
| `TestAuthRegister` | Success, missing fields, duplicate user, short password |
| `TestAuthLogin` | Success, wrong password, unknown user |
| `TestPets` | Create, list, status, feed, play, clean, multi-tenancy isolation, unauthenticated access |

---

## 9. Running Tests

```bash
# All tests, verbose
pytest tests/ -v

# Only unit tests
pytest tests/test_game.py -v

# Only integration tests
pytest tests/test_api.py -v

# Show a summary of passed/failed counts
pytest tests/ -q
```

---

## Further Reading

- [pytest documentation](https://docs.pytest.org/)
- [pytest fixtures guide](https://docs.pytest.org/en/latest/reference/fixtures.html)
- [Flask testing guide](https://flask.palletsprojects.com/en/latest/testing/)
- [unittest.mock documentation](https://docs.python.org/3/library/unittest.mock.html)
