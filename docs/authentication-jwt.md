# Authentication & JWT

Most web applications need to know *who* is making a request before they do anything sensitive. This project uses **JSON Web Tokens (JWTs)** to authenticate users. Before exploring JWTs, it is worth understanding how passwords are stored safely.

---

## 1. Never Store Passwords in Plain Text

If an attacker gains read access to your database (a SQL injection, a leaked backup, a misconfigured server), you do not want them to find cleartext passwords. The standard solution is a **password hash**.

A cryptographic hash function takes an input of any length and produces a fixed-length output (the hash). Critically, it is **one-way**: you cannot reverse a hash back to the original password.

```
password "hunter2"  →  hash function  →  "pbkdf2:sha256:260000$abc123..."
```

To check a login you hash the *submitted* password and compare it to the stored hash. If they match, the password is correct.

### How this project does it

`src/models.py` uses `werkzeug.security` (part of Flask's stack):

```python
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model):
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
```

`generate_password_hash` uses **PBKDF2-HMAC-SHA256** with a random salt by default — a battle-tested algorithm for password storage.

---

## 2. The Problem JWTs Solve

HTTP is **stateless** — every request arrives independently. A server does not remember who you are from one request to the next. Two traditional approaches exist:

1. **Sessions** — the server stores session state and gives the client a session ID cookie. Works well but requires server-side storage and does not scale as cleanly across multiple servers.
2. **Tokens** — the server creates a signed token containing the user's identity and gives it to the client. The client sends the token with every request. The server *verifies the signature* without looking anything up.

JWTs are the most common token format for REST APIs.

---

## 3. What is a JWT?

A JWT is a compact, URL-safe string with three Base64-encoded parts separated by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9   ← Header (algorithm & type)
.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIn0  ← Payload (claims)
.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c       ← Signature
```

**Header** — describes the signing algorithm (HS256 = HMAC-SHA256).

**Payload** — contains *claims* about the user (called "sub" for subject, plus any custom data). In this project the subject is the user's database ID.

**Signature** — `HMAC_SHA256(base64(header) + "." + base64(payload), SECRET_KEY)`. Only the server, which knows `JWT_SECRET_KEY`, can create or verify this signature.

> **Important**: the payload is *encoded*, not *encrypted*. Anyone can read the claims by Base64-decoding them. Never put sensitive data (passwords, credit cards) in a JWT payload.

---

## 4. Auth Flow in this Project

```
Client                                    Server
  │                                          │
  │  POST /api/auth/register                 │
  │  { username, email, password }  ────────▶│
  │                                          │ 1. Validate input
  │                                          │ 2. Hash password
  │                                          │ 3. Save user to DB
  │                                          │ 4. Create JWT signed with JWT_SECRET_KEY
  │◀──────────────────────────────  { user, access_token }
  │
  │  (store the token; e.g. in memory or localStorage)
  │
  │  POST /api/pets                          │
  │  Authorization: Bearer <token>  ────────▶│
  │                                          │ 1. Decode & verify signature
  │                                          │ 2. Extract user ID from payload
  │                                          │ 3. Run business logic
  │◀──────────────────────────────  { pet: {...} }
```

---

## 5. Registration (`src/routes/auth.py`)

```python
@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password =  data.get("password") or ""

    # Validation
    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    # Check for duplicates
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"error": "username or email already in use"}), 409

    # Create user
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Issue token  — identity is stored as a string
    token = create_access_token(identity=str(user.id))
    return jsonify({"user": user.to_dict(), "access_token": token}), 201
```

---

## 6. Login (`src/routes/auth.py`)

```python
@auth_bp.post("/login")
def login():
    data     = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password =  data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"user": user.to_dict(), "access_token": token}), 200
```

Notice the error message is deliberately vague ("invalid credentials") whether the username does not exist *or* the password is wrong. This prevents **username enumeration** — an attacker learning which usernames exist by checking whether the error says "user not found" vs "wrong password".

---

## 7. Protected Routes

The `@jwt_required()` decorator from Flask-JWT-Extended checks for a valid token:

```python
from flask_jwt_extended import get_jwt_identity, jwt_required

@pets_bp.get("")
@jwt_required()
def list_pets():
    user_id = int(get_jwt_identity())   # the subject claim from the token
    pets = Pet.query.filter_by(user_id=user_id).all()
    ...
```

If the `Authorization: Bearer <token>` header is missing or the token is invalid/expired, Flask-JWT-Extended automatically returns a 401 Unauthorized response.

---

## 8. Token Expiry

In `src/config.py`:

```python
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
```

Access tokens expire after 24 hours. After that, the client must log in again to get a new token. The test configuration uses 5 seconds to make expiry easy to test:

```python
class TestingConfig(Config):
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)
```

---

## 9. Security Best Practices Illustrated

| Practice | Where |
|----------|-------|
| Never store plain-text passwords | `set_password()` always hashes |
| Use a strong hashing algorithm (PBKDF2) | `generate_password_hash()` default |
| Keep secrets in environment variables | `JWT_SECRET_KEY = os.environ.get(...)` |
| Tokens expire | `JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)` |
| Vague error messages for auth failures | Login returns "invalid credentials" regardless of reason |
| Multi-tenancy isolation | Routes filter by `user_id` from the token, not from the request body |

---

## Further Reading

- [JWT.io — interactive JWT debugger and library list](https://jwt.io/)
- [Flask-JWT-Extended documentation](https://flask-jwt-extended.readthedocs.io/)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
