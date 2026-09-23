from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def reset_activity_participants(activity_name, original_participants):
    activities[activity_name]["participants"] = original_participants


def test_get_activities_returns_activity_catalog():
    # Arrange
    original = activities["Chess Club"]["participants"][:]

    try:
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert "Chess Club" in response.json()
        assert response.json()["Chess Club"]["participants"] == original
    finally:
        reset_activity_participants("Chess Club", original)


def test_signup_adds_participant_to_activity():
    # Arrange
    original = activities["Chess Club"]["participants"][:]
    email = "newstudent@example.com"

    try:
        # Act
        response = client.post("/activities/Chess%20Club/signup?email=newstudent@example.com")

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for Chess Club"
        assert email in activities["Chess Club"]["participants"]
    finally:
        reset_activity_participants("Chess Club", original)


def test_duplicate_signup_is_rejected():
    # Arrange
    original = activities["Chess Club"]["participants"][:]
    email = activities["Chess Club"]["participants"][0]

    try:
        # Act
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    finally:
        reset_activity_participants("Chess Club", original)


def test_unregister_removes_participant_from_activity():
    # Arrange
    original = activities["Chess Club"]["participants"][:]
    email = activities["Chess Club"]["participants"][0]

    try:
        # Act
        response = client.delete(f"/activities/Chess%20Club/participants/{email}")

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from Chess Club"
        assert email not in activities["Chess Club"]["participants"]
    finally:
        reset_activity_participants("Chess Club", original)


def test_unknown_activity_returns_404():
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post(f"/activities/Unknown%20Club/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
