"""
Integration tests for Mergington High School Activities API

Tests follow the Arrange-Act-Assert (AAA) pattern:
- Arrange: Set up test client and test data
- Act: Execute the API call
- Assert: Verify status code, response body, and side effects
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture providing a fresh TestClient with clean in-memory data for each test"""
    # Arrange: Reset activities to initial state for test isolation
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Competitive soccer team practicing tactics and fitness",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["alex@mergington.edu", "nina@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Skill development and friendly matches",
            "schedule": "Wednesdays and Fridays, 4:30 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "maya@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore drawing, painting, and mixed media projects",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["zoe@mergington.edu", "ryan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting, stagecraft, and production of school plays",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 25,
            "participants": ["sara@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Prepare for local and regional debate competitions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["victor@mergington.edu", "hana@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments and science fair projects",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabel@mergington.edu", "omar@mergington.edu"]
        }
    })
    
    # Create and return test client
    return TestClient(app)


class TestRootEndpoint:
    """Test suite for GET / endpoint"""

    def test_root_redirects_to_index(self, client):
        """Test that GET / redirects to /static/index.html"""
        # Act: Make request to root endpoint
        response = client.get("/", follow_redirects=False)

        # Assert: Verify redirect response
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivitiesEndpoint:
    """Test suite for GET /activities endpoint"""

    def test_get_all_activities_returns_success(self, client):
        """Test that GET /activities returns all activities with status 200"""
        # Act: Request all activities
        response = client.get("/activities")

        # Assert: Verify status and response structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9

    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have correct required fields"""
        # Act: Request all activities
        response = client.get("/activities")
        data = response.json()

        # Assert: Verify each activity has required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_has_expected_activities(self, client):
        """Test that all expected activities are present"""
        # Act: Request all activities
        response = client.get("/activities")
        data = response.json()

        # Assert: Verify expected activities exist
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Soccer Team",
            "Basketball Club",
            "Art Club",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_initial_participants(self, client):
        """Test that activities have initial participants"""
        # Act: Request all activities
        response = client.get("/activities")
        data = response.json()

        # Assert: Verify that at least some activities have participants
        activities_with_participants = [
            activity for activity in data.values()
            if len(activity["participants"]) > 0
        ]
        assert len(activities_with_participants) > 0


class TestSignupEndpoint:
    """Test suite for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_success(self, client):
        """Test successfully signing up a new student for an activity"""
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act: Sign up for activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify successful signup
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_student_appears_in_participants_list(self, client):
        """Test that signed-up student appears in activity participants"""
        # Arrange: Prepare test data
        activity_name = "Art Club"
        email = "newstudent@mergington.edu"

        # Act: Sign up and then retrieve activities
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        response = client.get("/activities")
        activities = response.json()

        # Assert: Verify student is in participants list
        assert email in activities[activity_name]["participants"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signing up for non-existent activity returns 404"""
        # Arrange: Prepare test data
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act: Attempt to sign up for non-existent activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify 404 response
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_400(self, client):
        """Test that duplicate signup attempts return 400"""
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club

        # Act: Attempt duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Verify 400 response for duplicate signup
        assert response.status_code == 400
        assert "Student already signed up" in response.json()["detail"]

    def test_signup_multiple_different_activities_success(self, client):
        """Test that a student can sign up for multiple different activities"""
        # Arrange: Prepare test data
        email = "student@mergington.edu"
        activities_to_join = ["Chess Club", "Art Club", "Science Club"]

        # Act: Sign up for multiple activities
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert: Verify student is in all activities
        response = client.get("/activities")
        activities = response.json()
        for activity_name in activities_to_join:
            assert email in activities[activity_name]["participants"]


class TestRemoveParticipantEndpoint:
    """Test suite for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_remove_existing_participant_success(self, client):
        """Test successfully removing a participant from an activity"""
        # Arrange: Prepare test data - use existing participant
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act: Remove participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert: Verify successful removal
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email in response.json()["message"]

    def test_removed_participant_not_in_list(self, client):
        """Test that removed participant no longer appears in activity"""
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act: Remove participant and then retrieve activities
        client.delete(f"/activities/{activity_name}/participants/{email}")
        response = client.get("/activities")
        activities = response.json()

        # Assert: Verify student is no longer in participants list
        assert email not in activities[activity_name]["participants"]

    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Test that removing from non-existent activity returns 404"""
        # Arrange: Prepare test data
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act: Attempt to remove from non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert: Verify 404 response
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_remove_nonexistent_participant_returns_404(self, client):
        """Test that removing non-existent participant returns 404"""
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act: Attempt to remove non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert: Verify 404 response
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_last_participant(self, client):
        """Test removing the last participant from an activity"""
        # Arrange: Add a single participant then remove them
        activity_name = "Art Club"
        email = "soloparticipant@mergington.edu"
        
        # First, get current participants and remove them
        response = client.get("/activities")
        current_participants = response.json()[activity_name]["participants"].copy()
        
        # Remove all current participants
        for participant in current_participants:
            client.delete(f"/activities/{activity_name}/participants/{participant}")
        
        # Add the solo participant
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act: Remove the last participant
        response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert: Verify successful removal and empty participants list
        assert response.status_code == 200
        response = client.get("/activities")
        assert len(response.json()[activity_name]["participants"]) == 0

    def test_remove_participant_multiple_times_returns_404(self, client):
        """Test that removing same participant twice returns 404 on second attempt"""
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act: Remove participant first time
        response1 = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        
        # Act: Attempt to remove same participant again
        response2 = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )

        # Assert: Verify first removal succeeds and second fails
        assert response1.status_code == 200
        assert response2.status_code == 404
        assert "Participant not found" in response2.json()["detail"]


class TestIntegrationScenarios:
    """Test suite for integration scenarios combining multiple operations"""

    def test_signup_then_remove_workflow(self, client):
        """Test complete workflow of signing up and then removing a participant"""
        # Arrange: Prepare test data
        activity_name = "Drama Club"
        email = "drama_student@mergington.edu"

        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200

        # Act: Verify in list
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]

        # Act: Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants/{email}"
        )
        assert remove_response.status_code == 200

        # Assert: Verify removed from list
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]

    def test_multiple_students_signup_and_remove(self, client):
        """Test multiple students signing up and removing from same activity"""
        # Arrange: Prepare test data
        activity_name = "Debate Team"
        students = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]

        # Act: All students sign up
        for email in students:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200

        # Assert: All in participants
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for email in students:
            assert email in participants

        # Act: Remove first student
        response = client.delete(
            f"/activities/{activity_name}/participants/{students[0]}"
        )
        assert response.status_code == 200

        # Assert: First removed, others still there
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        assert students[0] not in participants
        assert students[1] in participants
        assert students[2] in participants
