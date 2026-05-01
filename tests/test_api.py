"""Integration tests for REST API endpoints."""

import json

import pytest


def register_user(client, username="testuser", email="test@example.com", password="secret123"):
    return client.post(
        "/api/auth/register",
        data=json.dumps({"username": username, "email": email, "password": password}),
        content_type="application/json",
    )


def login_user(client, username="testuser", password="secret123"):
    return client.post(
        "/api/auth/login",
        data=json.dumps({"username": username, "password": password}),
        content_type="application/json",
    )


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


class TestAuthRegister:
    def test_register_success(self, client):
        resp = register_user(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert "access_token" in data
        assert data["user"]["username"] == "testuser"

    def test_register_missing_fields(self, client):
        resp = client.post(
            "/api/auth/register",
            data=json.dumps({"username": "only"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_register_duplicate_username(self, client):
        register_user(client)
        resp = register_user(client)
        assert resp.status_code == 409

    def test_register_short_password(self, client):
        resp = client.post(
            "/api/auth/register",
            data=json.dumps({"username": "u", "email": "u@e.com", "password": "abc"}),
            content_type="application/json",
        )
        assert resp.status_code == 400


class TestAuthLogin:
    def test_login_success(self, client):
        register_user(client)
        resp = login_user(client)
        assert resp.status_code == 200
        assert "access_token" in resp.get_json()

    def test_login_wrong_password(self, client):
        register_user(client)
        resp = login_user(client, password="wrongpassword")
        assert resp.status_code == 401

    def test_login_unknown_user(self, client):
        resp = login_user(client, username="nobody")
        assert resp.status_code == 401


class TestPets:
    def _setup(self, client):
        register_user(client)
        token = login_user(client).get_json()["access_token"]
        return token

    def test_create_pet(self, client):
        token = self._setup(client)
        resp = client.post(
            "/api/pets",
            data=json.dumps({"name": "Pikachu"}),
            content_type="application/json",
            headers=auth_header(token),
        )
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["pet"]["name"] == "Pikachu"

    def test_create_pet_no_name(self, client):
        token = self._setup(client)
        resp = client.post(
            "/api/pets",
            data=json.dumps({}),
            content_type="application/json",
            headers=auth_header(token),
        )
        assert resp.status_code == 400

    def test_list_pets(self, client):
        token = self._setup(client)
        client.post(
            "/api/pets",
            data=json.dumps({"name": "Pet1"}),
            content_type="application/json",
            headers=auth_header(token),
        )
        client.post(
            "/api/pets",
            data=json.dumps({"name": "Pet2"}),
            content_type="application/json",
            headers=auth_header(token),
        )
        resp = client.get("/api/pets", headers=auth_header(token))
        assert resp.status_code == 200
        assert len(resp.get_json()["pets"]) == 2

    def test_get_pet_status(self, client):
        token = self._setup(client)
        pet_id = client.post(
            "/api/pets",
            data=json.dumps({"name": "Rocky"}),
            content_type="application/json",
            headers=auth_header(token),
        ).get_json()["pet"]["id"]

        resp = client.get(f"/api/pets/{pet_id}", headers=auth_header(token))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["pet"]["name"] == "Rocky"

    def test_get_nonexistent_pet(self, client):
        token = self._setup(client)
        resp = client.get("/api/pets/9999", headers=auth_header(token))
        assert resp.status_code == 404

    def test_feed_pet(self, client):
        token = self._setup(client)
        pet = client.post(
            "/api/pets",
            data=json.dumps({"name": "Buddy"}),
            content_type="application/json",
            headers=auth_header(token),
        ).get_json()["pet"]
        initial_hunger = pet["hunger"]

        resp = client.post(f"/api/pets/{pet['id']}/feed", headers=auth_header(token))
        assert resp.status_code == 200
        new_hunger = resp.get_json()["pet"]["hunger"]
        assert new_hunger > initial_hunger

    def test_play_with_pet(self, client):
        token = self._setup(client)
        pet = client.post(
            "/api/pets",
            data=json.dumps({"name": "Buddy"}),
            content_type="application/json",
            headers=auth_header(token),
        ).get_json()["pet"]
        initial_happiness = pet["happiness"]

        resp = client.post(f"/api/pets/{pet['id']}/play", headers=auth_header(token))
        assert resp.status_code == 200
        new_happiness = resp.get_json()["pet"]["happiness"]
        assert new_happiness > initial_happiness

    def test_clean_pet(self, client):
        token = self._setup(client)
        pet = client.post(
            "/api/pets",
            data=json.dumps({"name": "Buddy"}),
            content_type="application/json",
            headers=auth_header(token),
        ).get_json()["pet"]

        resp = client.post(f"/api/pets/{pet['id']}/clean", headers=auth_header(token))
        assert resp.status_code == 200
        assert resp.get_json()["pet"]["cleanliness"] == 100.0

    def test_unauthenticated_access(self, client):
        resp = client.get("/api/pets")
        assert resp.status_code == 401

    def test_user_cannot_access_other_users_pet(self, client):
        # Register first user and create pet
        token1 = self._setup(client)
        pet_id = client.post(
            "/api/pets",
            data=json.dumps({"name": "SecretPet"}),
            content_type="application/json",
            headers=auth_header(token1),
        ).get_json()["pet"]["id"]

        # Register second user
        register_user(client, username="user2", email="user2@example.com")
        token2 = login_user(client, username="user2").get_json()["access_token"]

        resp = client.get(f"/api/pets/{pet_id}", headers=auth_header(token2))
        assert resp.status_code == 404
