from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert {
        "description",
        "schedule",
        "max_participants",
        "participants",
    } <= activities["Chess Club"].keys()


def test_signup_adds_participant():
    response = client.post(
        "/activities/Soccer Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up student@example.com for Soccer Club"
    }
    activities = client.get("/activities").json()
    assert "student@example.com" in activities["Soccer Club"]["participants"]


def test_duplicate_signup_is_rejected():
    email = "student@example.com"
    client.post("/activities/Soccer Club/signup", params={"email": email})

    response = client.post("/activities/Soccer Club/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    activities = client.get("/activities").json()
    assert activities["Soccer Club"]["participants"].count(email) == 1


def test_signup_for_unknown_activity_is_rejected():
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email():
    response = client.post("/activities/Soccer Club/signup")

    assert response.status_code == 422


def test_unregister_removes_participant():
    email = "student@example.com"
    client.post("/activities/Soccer Club/signup", params={"email": email})

    response = client.delete(
        "/activities/Soccer Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@example.com from Soccer Club"
    }
    activities = client.get("/activities").json()
    assert email not in activities["Soccer Club"]["participants"]


def test_unregistering_absent_participant_is_rejected():
    response = client.delete(
        "/activities/Soccer Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregistering_from_unknown_activity_is_rejected():
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": "student@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_requires_email():
    response = client.delete("/activities/Soccer Club/signup")

    assert response.status_code == 422