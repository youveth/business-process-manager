import os

os.environ["ADMIN_PASSWORD"] = "test-admin-password"
os.environ["USER_PASSWORD"] = "test-user-password"

import pytest

import app as app_module


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_database = tmp_path / "test.db"
    monkeypatch.setattr(app_module, "DATABASE", test_database)

    with app_module.app.app_context():
        app_module.init_db()

    app_module.app.config.update(TESTING=True)

    with app_module.app.test_client() as client:
        yield client


def login(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_login_page_is_accessible(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_admin_can_login(client):
    response = login(client, "admin", "test-admin-password")
    assert response.status_code == 200
    assert b"Business Process Manager" in response.data


def test_invalid_login_is_rejected(client):
    response = login(client, "admin", "wrong-password")
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_user_cannot_create_process(client):
    login(client, "user", "test-user-password")

    response = client.post(
        "/processes/new",
        data={
            "name": "Test Process",
            "description": "A test process",
            "owner": "IT",
            "steps": "Step one\nStep two",
        },
    )

    assert response.status_code == 403


def test_admin_can_create_process(client):
    login(client, "admin", "test-admin-password")

    response = client.post(
        "/processes/new",
        data={
            "name": "Test Process",
            "description": "A test process",
            "owner": "IT",
            "steps": "Step one\nStep two",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302

    with app_module.app.app_context():
        process = app_module.get_db().execute(
            "SELECT * FROM processes WHERE name = ?",
            ("Test Process",),
        ).fetchone()
        assert process is not None


def test_user_can_update_workflow_step(client):
    login(client, "user", "test-user-password")

    response = client.post(
        "/processes/1/steps/1/status",
        data={"status": "Completed"},
        follow_redirects=False,
    )

    assert response.status_code == 302

    with app_module.app.app_context():
        step = app_module.get_db().execute(
            "SELECT status FROM workflow_steps WHERE id = 1"
        ).fetchone()
        assert step["status"] == "Completed"


def test_api_processes_requires_login(client):
    response = client.get("/api/processes")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_api_processes_returns_json(client):
    login(client, "user", "test-user-password")

    response = client.get("/api/processes")

    assert response.status_code == 200
    data = response.get_json()
    assert "count" in data
    assert "processes" in data
    assert data["count"] == 2


def test_api_create_process_is_admin_only(client):
    login(client, "user", "test-user-password")

    response = client.post(
        "/api/processes",
        json={
            "name": "API Test",
            "description": "Created through the API",
            "owner": "IT",
            "steps": ["Create", "Review"],
        },
    )

    assert response.status_code == 403


def test_api_admin_can_create_process(client):
    login(client, "admin", "test-admin-password")

    response = client.post(
        "/api/processes",
        json={
            "name": "API Test",
            "description": "Created through the API",
            "owner": "IT",
            "steps": ["Create", "Review"],
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "API Test"
    assert len(data["steps"]) == 2


def test_api_rejects_invalid_step_status(client):
    login(client, "user", "test-user-password")

    response = client.patch(
        "/api/processes/1/steps/1/status",
        json={"status": "Unknown"},
    )

    assert response.status_code == 400


def test_delete_process_cascades_workflow_steps(client):
    login(client, "admin", "test-admin-password")

    with app_module.app.app_context():
        db = app_module.get_db()
        process = db.execute(
            "INSERT INTO processes (name, description, owner, status) VALUES (?, ?, ?, ?)",
            ("Delete Test", "Testing cascade delete", "IT", "Pending"),
        )
        process_id = process.lastrowid
        db.execute(
            "INSERT INTO workflow_steps (process_id, name, status, step_order) VALUES (?, ?, ?, ?)",
            (process_id, "Test step", "Pending", 1),
        )
        db.commit()

    response = client.delete(f"/api/processes/{process_id}")

    assert response.status_code == 200

    with app_module.app.app_context():
        db = app_module.get_db()
        assert db.execute(
            "SELECT id FROM processes WHERE id = ?", (process_id,)
        ).fetchone() is None
        assert db.execute(
            "SELECT id FROM workflow_steps WHERE process_id = ?", (process_id,)
        ).fetchone() is None
