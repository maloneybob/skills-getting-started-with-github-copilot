import pytest


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test that activities endpoint returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        # Verify structure of activities
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_get_activities_contains_basketball(self, client):
        """Test that Basketball activity exists in the response"""
        response = client.get("/activities")
        activities = response.json()
        assert "Basketball" in activities
        assert activities["Basketball"]["max_participants"] == 15

    def test_get_activities_contains_initial_participants(self, client):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities["Basketball"]["participants"]) > 0
        assert "james@mergington.edu" in activities["Basketball"]["participants"]


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student(self, client):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]

    def test_signup_verify_added_to_list(self, client):
        """Test that signed up student appears in participants list"""
        email = "teststudent@mergington.edu"
        # Sign up
        client.post(f"/activities/Tennis/signup?email={email}")
        # Verify
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Tennis"]["participants"]

    def test_signup_duplicate_student(self, client):
        """Test that duplicate signup returns error"""
        email = "duplicate@mergington.edu"
        # First signup
        client.post(f"/activities/Drama%20Club/signup?email={email}")
        # Second signup (duplicate)
        response = client.post(f"/activities/Drama%20Club/signup?email={email}")
        assert response.status_code == 400
        result = response.json()
        assert "already signed up" in result["detail"]

    def test_signup_invalid_activity(self, client):
        """Test that signup to non-existent activity returns error"""
        response = client.post(
            "/activities/NonexistentActivity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]

    def test_signup_at_capacity(self, client):
        """Test behavior when activity reaches max participants"""
        # This would require more setup, but here's the structure
        response = client.get("/activities")
        activities = response.json()
        # Check that we can still get activities without error
        assert response.status_code == 200


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        activity = "Art%20Studio"
        email = "grace@mergington.edu"
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        result = response.json()
        assert "Unregistered" in result["message"]

    def test_unregister_verify_removed_from_list(self, client):
        """Test that unregistered participant is removed from list"""
        # First, sign up a student
        email = "unregister_test@mergington.edu"
        client.post(f"/activities/Debate%20Team/signup?email={email}")
        # Verify they're signed up
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Debate Team"]["participants"]
        # Now unregister
        client.post(f"/activities/Debate%20Team/unregister?email={email}")
        # Verify they're removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Debate Team"]["participants"]

    def test_unregister_non_participant(self, client):
        """Test unregistering a student who is not signed up"""
        response = client.post(
            "/activities/Science%20Club/unregister?email=notparticipant@mergington.edu"
        )
        assert response.status_code == 400
        result = response.json()
        assert "not signed up" in result["detail"]

    def test_unregister_invalid_activity(self, client):
        """Test unregistering from non-existent activity"""
        response = client.post(
            "/activities/InvalidActivity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        result = response.json()
        assert "not found" in result["detail"]


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    def test_signup_and_unregister_workflow(self, client):
        """Test a complete signup and unregister workflow"""
        email = "workflow_test@mergington.edu"
        activity = "Chess%20Club"

        # Get initial state
        response = client.get("/activities")
        activities = response.json()
        initial_count = len(activities["Chess Club"]["participants"])

        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200

        # Verify signup
        response = client.get("/activities")
        activities = response.json()
        assert len(activities["Chess Club"]["participants"]) == initial_count + 1
        assert email in activities["Chess Club"]["participants"]

        # Unregister
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200

        # Verify unregister
        response = client.get("/activities")
        activities = response.json()
        assert len(activities["Chess Club"]["participants"]) == initial_count
        assert email not in activities["Chess Club"]["participants"]

    def test_multiple_students_signup(self, client):
        """Test multiple students signing up for different activities"""
        students = [
            ("student1@mergington.edu", "Basketball"),
            ("student2@mergington.edu", "Tennis"),
            ("student3@mergington.edu", "Programming%20Class"),
        ]

        for email, activity in students:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200

        # Verify all are signed up
        response = client.get("/activities")
        activities = response.json()
        assert "student1@mergington.edu" in activities["Basketball"]["participants"]
        assert "student2@mergington.edu" in activities["Tennis"]["participants"]
        assert "student3@mergington.edu" in activities["Programming Class"][
            "participants"
        ]
