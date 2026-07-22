import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


ORIGINAL_ACTIVITIES = copy.deepcopy(app_module.activities)
client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)
    yield
    app_module.activities = copy.deepcopy(ORIGINAL_ACTIVITIES)


def test_root_redirects_to_static_homepage():
    # Arrange
    request_path = "/"

    # Act
    response = client.get(request_path, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_activities_endpoint_disables_caching():
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)

    # Assert
    assert response.status_code == 200
    assert "no-store" in response.headers.get("cache-control", "")


def test_signup_for_activity_adds_participant_to_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    updated_response = client.get("/activities")
    assert email in updated_response.json()[activity_name]["participants"]


def test_signup_for_unknown_activity_returns_not_found():
    # Arrange
    activity_name = "Missing Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    updated_response = client.get("/activities")
    assert email not in updated_response.json()[activity_name]["participants"]


def test_unregister_for_missing_participant_returns_not_found():
    # Arrange
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
