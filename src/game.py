"""Core Tamagotchi APP° game logic."""

from datetime import datetime, timezone

# Stat decay rates per hour (how much each stat decreases every hour)
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


def _clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    """Clamp a value between min_val and max_val."""
    return max(min_val, min(max_val, value))


def apply_time_decay(pet) -> None:
    """
    Apply time-based stat decay to the pet based on time elapsed since last_updated.
    Updates the pet's stats in place. Does not commit to DB.
    """
    if not pet.is_alive:
        return

    now = datetime.now(timezone.utc)
    last = pet.last_updated

    # Make both datetimes timezone-aware for comparison
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)

    elapsed_hours = (now - last).total_seconds() / 3600.0

    if elapsed_hours <= 0:
        return

    # Decay stats
    pet.hunger = _clamp(pet.hunger - HUNGER_DECAY_PER_HOUR * elapsed_hours)
    pet.happiness = _clamp(pet.happiness - HAPPINESS_DECAY_PER_HOUR * elapsed_hours)
    pet.cleanliness = _clamp(pet.cleanliness - CLEANLINESS_DECAY_PER_HOUR * elapsed_hours)

    # Health decay based on poor stats
    poor_stat_count = sum([
        pet.hunger < HUNGER_CRITICAL_THRESHOLD,
        pet.happiness < HAPPINESS_CRITICAL_THRESHOLD,
        pet.cleanliness < CLEANLINESS_CRITICAL_THRESHOLD,
    ])
    if poor_stat_count > 0:
        pet.health = _clamp(pet.health - HEALTH_DECAY_PER_POOR_STAT * poor_stat_count * elapsed_hours)

    # Age the pet
    pet.age += int(elapsed_hours * AGE_GAIN_PER_HOUR)

    # Check if the pet has died
    if pet.health <= 0:
        pet.health = 0.0
        pet.is_alive = False

    pet.last_updated = now


def feed(pet) -> dict:
    """Feed the pet. Increases hunger (fullness) and slightly boosts happiness."""
    if not pet.is_alive:
        return {"success": False, "message": f"{pet.name} has passed away and cannot be fed."}

    apply_time_decay(pet)

    pet.hunger = _clamp(pet.hunger + FEED_HUNGER_GAIN)
    pet.happiness = _clamp(pet.happiness + FEED_HAPPINESS_GAIN)
    pet.last_updated = datetime.now(timezone.utc)

    return {
        "success": True,
        "message": f"{pet.name} enjoyed the meal!",
        "pet": pet.to_dict(),
    }


def play(pet) -> dict:
    """Play with the pet. Boosts happiness but costs some hunger."""
    if not pet.is_alive:
        return {"success": False, "message": f"{pet.name} has passed away and cannot play."}

    apply_time_decay(pet)

    pet.happiness = _clamp(pet.happiness + PLAY_HAPPINESS_GAIN)
    pet.hunger = _clamp(pet.hunger - PLAY_HUNGER_COST)
    pet.last_updated = datetime.now(timezone.utc)

    return {
        "success": True,
        "message": f"{pet.name} had a great time playing!",
        "pet": pet.to_dict(),
    }


def clean(pet) -> dict:
    """Clean the pet. Increases cleanliness."""
    if not pet.is_alive:
        return {"success": False, "message": f"{pet.name} has passed away and cannot be cleaned."}

    apply_time_decay(pet)

    pet.cleanliness = _clamp(pet.cleanliness + CLEAN_CLEANLINESS_GAIN)
    pet.last_updated = datetime.now(timezone.utc)

    return {
        "success": True,
        "message": f"{pet.name} is squeaky clean!",
        "pet": pet.to_dict(),
    }


def get_status(pet) -> dict:
    """Get the current status of the pet after applying time decay."""
    apply_time_decay(pet)
    return {
        "success": True,
        "pet": pet.to_dict(),
    }
