from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities as app_activities
from src.app import app


@pytest.fixture
def client():
    original_activities = deepcopy(app_activities)
    with TestClient(app) as test_client:
        yield test_client
    app_activities.clear()
    app_activities.update(original_activities)


def test_get_activities_returns_catalog(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_for_activity_adds_student(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in app_activities[activity_name]["participants"]


def test_signup_for_missing_activity_returns_404(client):
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_duplicate_student_returns_400(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name, safe='')}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}


def test_unsubscribe_student_removes_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/unsubscribe",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in app_activities[activity_name]["participants"]


def test_unsubscribe_missing_student_returns_400(client):
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name, safe='')}/unsubscribe",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student not signed up for this activity"}
