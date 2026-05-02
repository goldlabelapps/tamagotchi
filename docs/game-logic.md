# Game Logic

The Tamagotchi pet mechanics are implemented in `src/game.py` — a pure Python module with no Flask or database code. This separation makes the logic easy to read, reason about, and test independently.

## 1. Pet Stats

Every pet has four stats, each stored as a `float` in the range **0–100**:

| Stat | Starting value | Meaning |
|------|---------------|---------|
| `hunger` | 50 | 100 = full, 0 = starving |
| `happiness` | 50 | 100 = ecstatic, 0 = miserable |
| `cleanliness` | 100 | 100 = spotless, 0 = filthy |
| `health` | 100 | 100 = perfect, 0 = dead |

`health` is special — it does not decay on its own but is damaged when other stats fall into the critical zone.

## 2. Time-Based Decay

The app does not run a continuous background loop. Instead, every time a pet is accessed, `apply_time_decay()` calculates how much time has passed since the last update and applies the appropriate decay:

```python
HUNGER_DECAY_PER_HOUR    = 10.0
HAPPINESS_DECAY_PER_HOUR  = 8.0
CLEANLINESS_DECAY_PER_HOUR = 5.0
```

```python
def apply_time_decay(pet) -> None:
    if not pet.is_alive:
        return

    now  = datetime.now(timezone.utc)
    last = pet.last_updated
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)

    elapsed_hours = (now - last).total_seconds() / 3600.0
    if elapsed_hours <= 0:
        return

    pet.hunger      = _clamp(pet.hunger      - HUNGER_DECAY_PER_HOUR      * elapsed_hours)
    pet.happiness   = _clamp(pet.happiness   - HAPPINESS_DECAY_PER_HOUR   * elapsed_hours)
    pet.cleanliness = _clamp(pet.cleanliness - CLEANLINESS_DECAY_PER_HOUR * elapsed_hours)
    ...
```

### Why this approach?

- **No background jobs needed** — the server does not need to run a scheduler that wakes up every hour.
- **Accurate** — the calculation uses actual wall-clock time, so a pet that is not accessed for 3 hours decays by exactly 3 hours of stats.
- **Simple** — the math is just multiplication and clamping.

The trade-off is that a pet's stats in the database may be "stale" (not yet reflecting elapsed time) until someone fetches the pet. This is fine for a game — the stats are always accurate *at the moment you check them*.

## 3. Health Decay

When any stat falls below its critical threshold, `health` starts to decay:

```python
HUNGER_CRITICAL_THRESHOLD      = 20.0
HAPPINESS_CRITICAL_THRESHOLD   = 20.0
CLEANLINESS_CRITICAL_THRESHOLD = 20.0

HEALTH_DECAY_PER_POOR_STAT = 5.0  # health lost per hour per stat below threshold
```

```python
poor_stat_count = sum([
    pet.hunger      < HUNGER_CRITICAL_THRESHOLD,
    pet.happiness   < HAPPINESS_CRITICAL_THRESHOLD,
    pet.cleanliness < CLEANLINESS_CRITICAL_THRESHOLD,
])
if poor_stat_count > 0:
    pet.health = _clamp(pet.health - HEALTH_DECAY_PER_POOR_STAT * poor_stat_count * elapsed_hours)
```

`sum([True, False, True])` evaluates to `2` in Python because `True == 1` and `False == 0`. So if two stats are critical, health drops by `5 * 2 = 10` points per hour.

## 4. Aging

```python
AGE_GAIN_PER_HOUR = 1

pet.age += int(elapsed_hours * AGE_GAIN_PER_HOUR)
```

Age is measured in game-hours. A pet that was created 5 hours ago has `age = 5`.

## 5. Pet Death

```python
if pet.health <= 0:
    pet.health  = 0.0
    pet.is_alive = False
```

Once `health` hits zero the pet is marked `is_alive = False`. Dead pets cannot be fed, played with, or cleaned — every action checks for this first:

```python
def feed(pet) -> dict:
    if not pet.is_alive:
        return {"success": False, "message": f"{pet.name} has passed away and cannot be fed."}
    ...
```

## 6. The `_clamp` Helper

```python
def _clamp(value: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
    return max(min_val, min(max_val, value))
```

`_clamp` ensures a value never goes outside a valid range. Stats can never go below 0 or above 100. The leading underscore in `_clamp` is a Python convention meaning "private to this module — not part of the public API".

## 7. Actions and Their Effects

### Feed

```python
FEED_HUNGER_GAIN    = 30.0
FEED_HAPPINESS_GAIN  = 5.0
```

Feeding fills the pet up (hunger +30) and makes it a little happier (+5). The pet must be alive.

### Play

```python
PLAY_HAPPINESS_GAIN = 25.0
PLAY_HUNGER_COST    = 10.0
```

Playing boosts happiness (+25) but burns energy (hunger -10). The pet must be alive.

### Clean

```python
CLEAN_CLEANLINESS_GAIN = 40.0
```

Cleaning improves cleanliness (+40). The pet must be alive.

### Get Status

`get_status()` applies time decay and returns the current pet state without making any other change. Every `GET /api/pets/<id>` request calls this so the returned stats are always up to date.

## 8. Return Values

Every action function returns a dictionary:

```python
# Success
{
    "success": True,
    "message": "Pikachu enjoyed the meal!",
    "pet": { ... pet.to_dict() ... }
}

# Failure (dead pet)
{
    "success": False,
    "message": "Pikachu has passed away and cannot be fed."
}
```

The route handlers use `result["success"]` to pick the HTTP status code:

```python
status_code = 200 if result["success"] else 409
return jsonify(result), status_code
```

## 9. Decay Timeline Example

Suppose a pet starts with `hunger=50`, `happiness=50`, `cleanliness=100`, `health=100` and is not touched for **6 hours**:

| Stat | Decay rate | After 6 h |
|------|-----------|-----------|
| hunger | 10/h | `50 - 60 = 0` (clamped) |
| happiness | 8/h | `50 - 48 = 2` |
| cleanliness | 5/h | `100 - 30 = 70` |

`hunger=0 < 20` → poor stat (1 count)  
`happiness=2 < 20` → poor stat (2 count)  
`cleanliness=70 ≥ 20` → ok

Health decays at `5 * 2 counts * 6 h = 60` → `100 - 60 = 40`

After **another 2 hours** with no interaction:

| Stat | After 8 h total |
|------|----------------|
| hunger | 0 (clamped) |
| happiness | 0 (clamped) |
| cleanliness | `100 - 40 = 60` |

All three might be below threshold now, so health decays faster. Eventually `health` reaches 0 and the pet dies.

## 10. Design Philosophy

The game constants are defined at the top of `game.py` as module-level variables with clear names. This makes it easy to tune the game balance without hunting for magic numbers buried in logic:

```python
HUNGER_DECAY_PER_HOUR    = 10.0   # change this to make the pet hungrier/slower
HAPPINESS_DECAY_PER_HOUR  = 8.0
...
```
