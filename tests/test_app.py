import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the activities state after each test to prevent cross-test pollution."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    # Arrange: (no setup needed — default data is provided by the fixture)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_non_empty_dict():
    # Arrange: (no setup needed)

    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_activities_entries_have_required_fields():
    # Arrange: (no setup needed)

    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success_returns_200_with_message():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant_to_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email in participants


def test_signup_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_signup_duplicate_email_returns_400():
    # Arrange — michael is already enrolled in Chess Club in the seed data
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success_returns_200_with_message():
    # Arrange — michael is already enrolled in Chess Club in the seed data
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant_from_activity():
    # Arrange — michael is already enrolled in Chess Club in the seed data
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404


def test_unregister_not_enrolled_returns_404():
    # Arrange
    activity_name = "Chess Club"
    email = "notenrolled@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
