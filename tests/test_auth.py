from app import create_app


def test_session_initially_anonymous():
    app = create_app({"TESTING": True, "SECRET_KEY": "test"})
    client = app.test_client()

    response = client.get("/api/auth/session")

    assert response.status_code == 200
    assert response.json["ok"] is True
    assert response.json["authenticated"] is False


def test_login_requires_username_and_password():
    app = create_app({"TESTING": True, "SECRET_KEY": "test"})
    client = app.test_client()

    response = client.post("/api/auth/login", json={"username": "", "password": ""})

    assert response.status_code == 400
    assert response.json["ok"] is False
