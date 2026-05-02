# API Reference

Complete reference for every endpoint in the Tamagotchi APP° REST API.

All requests and responses use **JSON** (`Content-Type: application/json`).  
Protected endpoints require the `Authorization: Bearer <token>` header.

## Base URL

| Environment | Base URL |
|-------------|----------|
| Local development | `http://localhost:5555` |
| Production (Render) | `https://<your-service>.onrender.com` |

## Authentication

### POST `/api/auth/register`

Create a new user account. Returns a JWT access token.

**Request body**

```json
{
  "username": "alice",
  "email":    "alice@example.com",
  "password": "hunter2secret"
}
```

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `username` | string | ✅ | Must be unique |
| `email` | string | ✅ | Must be unique |
| `password` | string | ✅ | Minimum 6 characters |

**Responses**

`201 Created`
```json
{
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2025-01-01T12:00:00+00:00"
  },
  "access_token": "eyJhbGci..."
}
```

`400 Bad Request` — missing fields or password too short
```json
{ "error": "username, email, and password are required" }
```

`409 Conflict` — username or email already in use
```json
{ "error": "username or email already in use" }
```

### POST `/api/auth/login`

Log in with an existing account. Returns a JWT access token.

**Request body**

```json
{
  "username": "alice",
  "password": "hunter2secret"
}
```

**Responses**

`200 OK`
```json
{
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2025-01-01T12:00:00+00:00"
  },
  "access_token": "eyJhbGci..."
}
```

`400 Bad Request` — missing fields
```json
{ "error": "username and password are required" }
```

`401 Unauthorized` — wrong username or password
```json
{ "error": "invalid credentials" }
```

## Pets

All pet endpoints require authentication: include the JWT token in the `Authorization` header.

```
Authorization: Bearer eyJhbGci...
```

### POST `/api/pets`

Create a new virtual pet for the authenticated user.

**Request body**

```json
{ "name": "Pikachu" }
```

**Responses**

`201 Created`
```json
{
  "pet": {
    "id": 1,
    "user_id": 1,
    "name": "Pikachu",
    "age": 0,
    "hunger": 50.0,
    "happiness": 50.0,
    "cleanliness": 100.0,
    "health": 100.0,
    "is_alive": true,
    "last_updated": "2025-01-01T12:00:00+00:00",
    "created_at": "2025-01-01T12:00:00+00:00"
  }
}
```

`400 Bad Request` — name missing
```json
{ "error": "pet name is required" }
```

`401 Unauthorized` — no or invalid token

### GET `/api/pets`

List all pets belonging to the authenticated user. Time decay is **not** applied on this endpoint (stats may be slightly stale).

Returns JSON when `Accept: application/json`; returns HTML when `Accept: text/html` (e.g. a browser).

**Response** `200 OK`

```json
{
  "pets": [
    {
      "id": 1,
      "user_id": 1,
      "name": "Pikachu",
      "age": 2,
      "hunger": 30.0,
      "happiness": 34.0,
      "cleanliness": 90.0,
      "health": 100.0,
      "is_alive": true,
      "last_updated": "2025-01-01T14:00:00+00:00",
      "created_at": "2025-01-01T12:00:00+00:00"
    }
  ]
}
```

`401 Unauthorized` — no or invalid token

### GET `/api/pets/<id>`

Get the current status of a specific pet. **Time decay is applied** and saved to the database before returning stats.

Returns JSON or HTML depending on the `Accept` header.

**URL parameter**: `id` — integer pet ID

**Response** `200 OK`

```json
{
  "success": true,
  "pet": {
    "id": 1,
    "user_id": 1,
    "name": "Pikachu",
    "age": 3,
    "hunger": 20.0,
    "happiness": 26.0,
    "cleanliness": 85.0,
    "health": 100.0,
    "is_alive": true,
    "last_updated": "2025-01-01T15:00:00+00:00",
    "created_at": "2025-01-01T12:00:00+00:00"
  }
}
```

`401 Unauthorized` — no or invalid token  
`404 Not Found` — pet does not exist or belongs to another user

### POST `/api/pets/<id>/feed`

Feed the pet. Increases hunger by 30 and happiness by 5.

**URL parameter**: `id` — integer pet ID  
**Request body**: none required

**Response** `200 OK` (pet alive)

```json
{
  "success": true,
  "message": "Pikachu enjoyed the meal!",
  "pet": { ... }
}
```

**Response** `409 Conflict` (pet is dead)

```json
{
  "success": false,
  "message": "Pikachu has passed away and cannot be fed."
}
```

`401 Unauthorized` — no or invalid token  
`404 Not Found` — pet not found

### POST `/api/pets/<id>/play`

Play with the pet. Increases happiness by 25; decreases hunger by 10.

**URL parameter**: `id` — integer pet ID  
**Request body**: none required

**Response** `200 OK` (pet alive)

```json
{
  "success": true,
  "message": "Pikachu had a great time playing!",
  "pet": { ... }
}
```

**Response** `409 Conflict` (pet is dead)

```json
{
  "success": false,
  "message": "Pikachu has passed away and cannot play."
}
```

`401 Unauthorized` — no or invalid token  
`404 Not Found` — pet not found

### POST `/api/pets/<id>/clean`

Clean the pet. Increases cleanliness by 40.

**URL parameter**: `id` — integer pet ID  
**Request body**: none required

**Response** `200 OK` (pet alive)

```json
{
  "success": true,
  "message": "Pikachu is squeaky clean!",
  "pet": { ... }
}
```

**Response** `409 Conflict` (pet is dead)

```json
{
  "success": false,
  "message": "Pikachu has passed away and cannot be cleaned."
}
```

`401 Unauthorized` — no or invalid token  
`404 Not Found` — pet not found

## Pet Object Schema

All pet endpoints return a pet object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique pet identifier |
| `user_id` | integer | ID of the owner |
| `name` | string | Pet's name |
| `age` | integer | Age in game-hours |
| `hunger` | float (0–100) | 100 = full, 0 = starving |
| `happiness` | float (0–100) | 100 = ecstatic, 0 = miserable |
| `cleanliness` | float (0–100) | 100 = spotless, 0 = filthy |
| `health` | float (0–100) | 0 = dead |
| `is_alive` | boolean | `false` once health reaches 0 |
| `last_updated` | ISO 8601 string | When stats were last calculated |
| `created_at` | ISO 8601 string | When the pet was created |

## Stat Decay Constants

| Stat | Decays by (per hour) | Critical threshold | Effect when critical |
|------|---------------------|--------------------|---------------------|
| `hunger` | 10 | < 20 | Health decays by 5/hr per critical stat |
| `happiness` | 8 | < 20 | Health decays by 5/hr per critical stat |
| `cleanliness` | 5 | < 20 | Health decays by 5/hr per critical stat |
| `health` | 0 (indirect) | 0 | Pet dies (`is_alive = false`) |

## Action Effects Summary

| Action | Endpoint | Effect |
|--------|----------|--------|
| Feed | `POST /api/pets/<id>/feed` | hunger +30, happiness +5 |
| Play | `POST /api/pets/<id>/play` | happiness +25, hunger -10 |
| Clean | `POST /api/pets/<id>/clean` | cleanliness +40 |

All stats are clamped to the range **0–100** after each action.
