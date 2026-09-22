from copy import deepcopy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def reset_activities():
    original_state = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_state))


def ensure_email_not_registered(activity_name, email):
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)


def assert_error_response(response, expected_status, expected_detail):
    assert response.status_code == expected_status
    assert response.json()["detail"] == expected_detail


def test_get_activities_returns_all_activity_data(client, reset_activities):
    # Arrange
    expected_keys = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert expected_keys.issubset(payload.keys())
    assert "participants" in payload["Chess Club"]


def test_signup_for_activity_registers_new_student(client, reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    ensure_email_not_registered(activity_name, email)

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_rejects_duplicate_email(client, reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")

    # Assert
    assert_error_response(response, 400, "Student already signed up for this activity")


def test_signup_for_missing_activity_returns_404(client, reset_activities):
    # Arrange
    activity_name = "Unknown Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")

    # Assert
    assert_error_response(response, 404, "Activity not found")


def test_delete_participant_removes_student_from_activity(client, reset_activities):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    ensure_email_not_registered(activity_name, email)

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup?email={quote(email)}"
    )

    # Assert
    assert signup_response.status_code == 200
    assert email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{quote(email)}"
    )

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Removed {email} from {activity_name}"


def test_delete_participant_for_missing_student_returns_404(client, reset_activities):
    # Arrange
    activity_name = "Gym Class"
    email = "missingstudent@mergington.edu"
    ensure_email_not_registered(activity_name, email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{quote(email)}"
    )

    # Assert
    assert_error_response(response, 404, "Participant not found")
