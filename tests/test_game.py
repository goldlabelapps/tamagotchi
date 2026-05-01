"""Unit tests for core game logic."""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from src import game as game_logic
from src.game import (
    CLEAN_CLEANLINESS_GAIN,
    FEED_HAPPINESS_GAIN,
    FEED_HUNGER_GAIN,
    PLAY_HAPPINESS_GAIN,
    PLAY_HUNGER_COST,
    apply_time_decay,
    clean,
    feed,
    get_status,
    play,
)


def make_pet(name="Buddy", hunger=50.0, happiness=50.0, cleanliness=100.0, health=100.0, is_alive=True):
    """Create a mock pet object."""
    pet = MagicMock()
    pet.name = name
    pet.hunger = hunger
    pet.happiness = happiness
    pet.cleanliness = cleanliness
    pet.health = health
    pet.is_alive = is_alive
    pet.age = 0
    pet.last_updated = datetime.now(timezone.utc)
    pet.to_dict.return_value = {
        "id": 1,
        "name": name,
        "hunger": hunger,
        "happiness": happiness,
        "cleanliness": cleanliness,
        "health": health,
        "is_alive": is_alive,
    }
    return pet


class TestApplyTimeDecay:
    def test_no_decay_when_just_updated(self):
        pet = make_pet()
        original_hunger = pet.hunger
        apply_time_decay(pet)
        # Almost no time has passed so stats should be nearly unchanged
        assert abs(pet.hunger - original_hunger) < 0.01

    def test_hunger_decays_over_time(self):
        pet = make_pet(hunger=80.0)
        pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=2)
        apply_time_decay(pet)
        expected = 80.0 - game_logic.HUNGER_DECAY_PER_HOUR * 2
        assert abs(pet.hunger - expected) < 0.5

    def test_happiness_decays_over_time(self):
        pet = make_pet(happiness=80.0)
        pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=2)
        apply_time_decay(pet)
        expected = 80.0 - game_logic.HAPPINESS_DECAY_PER_HOUR * 2
        assert abs(pet.happiness - expected) < 0.5

    def test_cleanliness_decays_over_time(self):
        pet = make_pet(cleanliness=80.0)
        pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=2)
        apply_time_decay(pet)
        expected = 80.0 - game_logic.CLEANLINESS_DECAY_PER_HOUR * 2
        assert abs(pet.cleanliness - expected) < 0.5

    def test_stats_clamp_at_zero(self):
        pet = make_pet(hunger=5.0, happiness=5.0, cleanliness=5.0)
        pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=24)
        apply_time_decay(pet)
        assert pet.hunger >= 0.0
        assert pet.happiness >= 0.0
        assert pet.cleanliness >= 0.0

    def test_pet_dies_when_health_reaches_zero(self):
        pet = make_pet(hunger=0.0, happiness=0.0, cleanliness=0.0, health=1.0)
        pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=10)
        apply_time_decay(pet)
        assert pet.health == 0.0
        assert pet.is_alive is False

    def test_dead_pet_not_decayed(self):
        pet = make_pet(hunger=100.0, is_alive=False)
        pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=5)
        original_hunger = pet.hunger
        apply_time_decay(pet)
        assert pet.hunger == original_hunger

    def test_age_increases_over_time(self):
        pet = make_pet()
        pet.last_updated = datetime.now(timezone.utc) - timedelta(hours=3)
        apply_time_decay(pet)
        assert pet.age >= 3


class TestFeed:
    def test_feed_increases_hunger(self):
        pet = make_pet(hunger=40.0)
        result = feed(pet)
        assert result["success"] is True
        assert pet.hunger == pytest.approx(40.0 + FEED_HUNGER_GAIN, abs=0.5)

    def test_feed_increases_happiness(self):
        pet = make_pet(happiness=40.0)
        result = feed(pet)
        assert result["success"] is True
        assert pet.happiness == pytest.approx(40.0 + FEED_HAPPINESS_GAIN, abs=0.5)

    def test_feed_clamps_hunger_at_100(self):
        pet = make_pet(hunger=90.0)
        feed(pet)
        assert pet.hunger <= 100.0

    def test_feed_dead_pet_fails(self):
        pet = make_pet(is_alive=False)
        result = feed(pet)
        assert result["success"] is False
        assert "passed away" in result["message"]


class TestPlay:
    def test_play_increases_happiness(self):
        pet = make_pet(happiness=40.0)
        result = play(pet)
        assert result["success"] is True
        assert pet.happiness == pytest.approx(40.0 + PLAY_HAPPINESS_GAIN, abs=0.5)

    def test_play_costs_hunger(self):
        pet = make_pet(hunger=60.0)
        result = play(pet)
        assert result["success"] is True
        assert pet.hunger == pytest.approx(60.0 - PLAY_HUNGER_COST, abs=0.5)

    def test_play_clamps_hunger_at_zero(self):
        pet = make_pet(hunger=5.0)
        play(pet)
        assert pet.hunger >= 0.0

    def test_play_dead_pet_fails(self):
        pet = make_pet(is_alive=False)
        result = play(pet)
        assert result["success"] is False
        assert "passed away" in result["message"]


class TestClean:
    def test_clean_increases_cleanliness(self):
        pet = make_pet(cleanliness=30.0)
        result = clean(pet)
        assert result["success"] is True
        assert pet.cleanliness == pytest.approx(30.0 + CLEAN_CLEANLINESS_GAIN, abs=0.5)

    def test_clean_clamps_cleanliness_at_100(self):
        pet = make_pet(cleanliness=90.0)
        clean(pet)
        assert pet.cleanliness <= 100.0

    def test_clean_dead_pet_fails(self):
        pet = make_pet(is_alive=False)
        result = clean(pet)
        assert result["success"] is False
        assert "passed away" in result["message"]


class TestGetStatus:
    def test_get_status_returns_pet_dict(self):
        pet = make_pet()
        result = get_status(pet)
        assert result["success"] is True
        assert "pet" in result
