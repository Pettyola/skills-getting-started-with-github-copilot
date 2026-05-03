import pytest


class TestGetActivities:
    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        # Arrange
        # No setup needed - we're just calling the endpoint
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_activities_have_required_fields(self, client):
        """Test that activities have required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Field '{field}' missing in {activity_name}"
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    def test_signup_successful(self, client, sample_activity):
        """Test successful signup for an activity"""
        # Arrange
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{sample_activity}/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_activity_not_found(self, client, sample_email):
        """Test signup for non-existent activity"""
        # Arrange
        invalid_activity = "NonExistentActivity"
        
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={sample_email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_duplicate_prevention(self, client, sample_activity, sample_email):
        """Test that duplicate signup is prevented"""
        # Arrange
        email = sample_email
        activity = sample_activity
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert first signup succeeds
        assert response1.status_code == 200
        
        # Act - Try to signup again with same email
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Assert duplicate signup is prevented
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_email_added_to_participants(self, client, sample_activity, sample_email):
        """Test that email is added to activity participants"""
        # Arrange
        email = sample_email
        activity = sample_activity
        
        # Get initial participants count
        get_response = client.get("/activities")
        initial_count = len(get_response.json()[activity]["participants"])
        
        # Act - Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert - participants count increased
        get_response_after = client.get("/activities")
        new_count = len(get_response_after.json()[activity]["participants"])
        assert new_count == initial_count + 1
        assert email in get_response_after.json()[activity]["participants"]


class TestUnregister:
    def test_unregister_successful(self, client, sample_activity, sample_email):
        """Test successful unregistration from an activity"""
        # Arrange - First sign up
        email = sample_email
        activity = sample_activity
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Act - Unregister
        response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_activity_not_found(self, client, sample_email):
        """Test unregister for non-existent activity"""
        # Arrange
        invalid_activity = "NonExistentActivity"
        
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/unregister?email={sample_email}"
        )
        
        # Assert
        assert response.status_code == 404

    def test_unregister_student_not_registered(self, client, sample_activity):
        """Test unregister when student is not registered"""
        # Arrange
        unregistered_email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{sample_activity}/unregister?email={unregistered_email}"
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_removes_from_participants(self, client, sample_activity, sample_email):
        """Test that email is removed from activity participants"""
        # Arrange - Sign up first
        email = sample_email
        activity = sample_activity
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get count before unregister
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity]["participants"])
        
        # Act - Unregister
        client.delete(f"/activities/{activity}/unregister?email={email}")
        
        # Assert - participants count decreased
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity]["participants"])
        assert count_after == count_before - 1
        assert email not in response_after.json()[activity]["participants"]
