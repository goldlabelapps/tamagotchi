from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    pets = db.relationship("Pet", backref="owner", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Pet(db.Model):
    __tablename__ = "pets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    age = db.Column(db.Integer, default=0)
    hunger = db.Column(db.Float, default=50.0)       # 0 = starving, 100 = full
    happiness = db.Column(db.Float, default=50.0)    # 0 = miserable, 100 = ecstatic
    cleanliness = db.Column(db.Float, default=100.0) # 0 = filthy, 100 = spotless
    health = db.Column(db.Float, default=100.0)      # 0 = dead, 100 = perfect
    is_alive = db.Column(db.Boolean, default=True)
    last_updated = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "age": self.age,
            "hunger": round(self.hunger, 1),
            "happiness": round(self.happiness, 1),
            "cleanliness": round(self.cleanliness, 1),
            "health": round(self.health, 1),
            "is_alive": self.is_alive,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
