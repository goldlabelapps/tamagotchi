import pytest

from src.app import create_app
from src.config import TestingConfig
from src.models import db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    """Roll back DB changes after each test."""
    with app.app_context():
        yield
        _db.session.remove()
        # Truncate all tables
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
