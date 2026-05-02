# REST APIs

The Tamagotchi app is a **REST API**. Understanding what that means — and the conventions that come with it — will help you read the route code and write clients that consume it.

---

## 1. What is an API?

An **API** (Application Programming Interface) is a defined way for two programs to talk to each other. A **web API** uses HTTP as the communication channel: the client sends an HTTP request; the server processes it and sends an HTTP response.

Examples of clients for this API:
- A JavaScript front-end in a browser
- A mobile app
- `curl` in a terminal
- A Python script using the `requests` library
- The automated tests in `tests/test_api.py`

---

## 2. HTTP in Brief

Every HTTP transaction has a **request** and a **response**.

### Request structure

```
POST /api/auth/login HTTP/1.1
Host: tamagotchi.onrender.com
Content-Type: application/json
Authorization: Bearer eyJhbGci...

{"username": "alice", "password": "hunter2"}
```

| Part | Meaning |
|------|---------|
| **Method** (`POST`) | What action to perform |
| **Path** (`/api/auth/login`) | Which resource to act on |
| **Headers** | Metadata (content type, auth token, …) |
| **Body** | Optional data sent with the request (JSON here) |

### Response structure

```
HTTP/1.1 200 OK
Content-Type: application/json

{"user": {"id": 1, "username": "alice"}, "access_token": "eyJhbGci..."}
```

| Part | Meaning |
|------|---------|
| **Status code** (`200`) | Whether the request succeeded and how |
| **Headers** | Metadata about the response |
| **Body** | The data returned (JSON here) |

---

## 3. HTTP Methods

REST uses different HTTP methods to convey intent:

| Method | Meaning | Typical use |
|--------|---------|-------------|
| `GET` | Read a resource | List pets, get one pet's status |
| `POST` | Create a resource, or trigger an action | Create a pet, feed a pet |
| `PUT` | Replace a resource entirely | (not used in this project) |
| `PATCH` | Partially update a resource | (not used in this project) |
| `DELETE` | Remove a resource | (not used in this project) |

In Flask, method-specific decorators make this explicit:

```python
@pets_bp.get("")           # GET  /api/pets
@pets_bp.post("")          # POST /api/pets
@pets_bp.post("/<int:pet_id>/feed")   # POST /api/pets/42/feed
```

---

## 4. Status Codes

HTTP status codes are three-digit numbers grouped by category:

| Range | Category | Common codes |
|-------|----------|-------------|
| 2xx | Success | `200 OK`, `201 Created` |
| 4xx | Client error (you did something wrong) | `400 Bad Request`, `401 Unauthorized`, `404 Not Found`, `409 Conflict` |
| 5xx | Server error (the server broke) | `500 Internal Server Error` |

### Status codes used in this project

| Code | Meaning | When used |
|------|---------|-----------|
| `200 OK` | Request succeeded | Successful GET or action |
| `201 Created` | Resource created | Register, create pet |
| `400 Bad Request` | Invalid input | Missing required fields |
| `401 Unauthorized` | Not authenticated | No/invalid token |
| `404 Not Found` | Resource does not exist | Pet ID not found |
| `409 Conflict` | Conflict with current state | Duplicate username; acting on dead pet |

---

## 5. JSON

**JSON** (JavaScript Object Notation) is the standard data format for REST APIs. It maps directly to Python data structures:

| JSON | Python |
|------|--------|
| `{"key": "value"}` | `dict` |
| `[1, 2, 3]` | `list` |
| `"hello"` | `str` |
| `42` | `int` |
| `3.14` | `float` |
| `true` / `false` | `True` / `False` |
| `null` | `None` |

Flask reads JSON from a request with:

```python
data = request.get_json(silent=True) or {}
```

And writes JSON to a response with:

```python
return jsonify({"pet": pet.to_dict()}), 200
```

---

## 6. REST Conventions

REST is an architectural *style*, not a strict standard. The conventions used in this project are common across the industry:

### Resource-based URLs

URLs represent *nouns* (things), not *verbs* (actions):

```
/api/pets           ← the collection of pets
/api/pets/42        ← pet with ID 42
/api/pets/42/feed   ← a sub-resource action on pet 42
```

### Statelessness

Every request contains all the information the server needs to process it. The server stores no client session state between requests. The JWT token carries the user's identity *inside* each request.

### Predictable structure

GET the collection → list of resources  
POST the collection → create a new resource  
GET a single resource → get its details  
POST an action on a resource → perform that action  

---

## 7. Calling the API — Examples

Using `curl`:

```bash
# Register
curl -X POST http://localhost:5555/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret123"}'

# Login (save the token)
TOKEN=$(curl -s -X POST http://localhost:5555/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}' | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Create a pet
curl -X POST http://localhost:5555/api/pets \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"Pikachu"}'

# List pets
curl http://localhost:5555/api/pets \
  -H "Authorization: Bearer $TOKEN"

# Feed a pet (replace 1 with the actual pet ID)
curl -X POST http://localhost:5555/api/pets/1/feed \
  -H "Authorization: Bearer $TOKEN"
```

Using Python's `requests` library:

```python
import requests

BASE = "http://localhost:5555"

# Register
r = requests.post(f"{BASE}/api/auth/register", json={
    "username": "alice", "email": "alice@example.com", "password": "secret123"
})
token = r.json()["access_token"]

headers = {"Authorization": f"Bearer {token}"}

# Create a pet
pet = requests.post(f"{BASE}/api/pets", json={"name": "Pikachu"}, headers=headers).json()["pet"]

# Feed the pet
result = requests.post(f"{BASE}/api/pets/{pet['id']}/feed", headers=headers).json()
print(result["message"])   # "Pikachu enjoyed the meal!"
```

---

## 8. The `Authorization` Header

Protected routes require the token to be sent in the `Authorization` header using the **Bearer** scheme:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Flask-JWT-Extended reads this header automatically when a route is decorated with `@jwt_required()`.

---

## Further Reading

- [MDN — HTTP overview](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview)
- [REST API tutorial](https://restfulapi.net/)
- [HTTP status codes reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
