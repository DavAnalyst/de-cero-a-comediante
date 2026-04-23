import json


def _register(client, email="user@test.com", name="Test User", password="password123"):
    return client.post(
        "/api/auth/register",
        data=json.dumps({"email": email, "name": name, "password": password}),
        content_type="application/json",
    )


def _login(client, email="user@test.com", password="password123"):
    return client.post(
        "/api/auth/login",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json",
    )


def test_register_success(client):
    rv = _register(client)
    assert rv.status_code == 201
    data = rv.get_json()
    assert "token" in data
    assert data["user"]["email"] == "user@test.com"


def test_register_duplicate_email(client):
    _register(client)
    rv = _register(client)
    assert rv.status_code == 409


def test_register_short_password(client):
    rv = _register(client, password="short")
    assert rv.status_code == 400


def test_login_success(client):
    _register(client)
    rv = _login(client)
    assert rv.status_code == 200
    assert "token" in rv.get_json()


def test_login_wrong_password(client):
    _register(client)
    rv = _login(client, password="wrongpassword")
    assert rv.status_code == 401


def test_me_requires_auth(client):
    rv = client.get("/api/auth/me")
    assert rv.status_code == 401


def test_me_with_token(client):
    rv = _register(client)
    token = rv.get_json()["token"]
    rv2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert rv2.status_code == 200
    assert rv2.get_json()["email"] == "user@test.com"
