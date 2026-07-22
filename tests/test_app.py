from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_email_from_activity():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    initial_response = client.get("/activities")
    assert initial_response.status_code == 200
    initial_participants = initial_response.json()[activity_name]["participants"]
    assert email in initial_participants

    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    updated_response = client.get("/activities")
    updated_participants = updated_response.json()[activity_name]["participants"]
    assert email not in updated_participants


def test_activities_endpoint_disables_caching():
    response = client.get("/activities")

    assert response.status_code == 200
    assert "no-store" in response.headers.get("cache-control", "")
