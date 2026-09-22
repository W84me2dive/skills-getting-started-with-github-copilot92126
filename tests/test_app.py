from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


def test_delete_participant_removes_student_from_activity():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={quote(email)}"
    )
    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]

    response = client.delete(
        f"/activities/{activity_name}/participants/{quote(email)}"
    )

    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Removed {email} from {activity_name}"


def test_delete_participant_for_missing_student_returns_404():
    activity_name = "Gym Class"
    email = "missingstudent@mergington.edu"

    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.delete(
        f"/activities/{activity_name}/participants/{quote(email)}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
