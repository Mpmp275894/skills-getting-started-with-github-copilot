import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test retrieving all activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        for activity in expected_activities:
            assert activity in data
    
    def test_activities_have_correct_structure(self, client):
        """Test that activities have required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_details in data.items():
            for field in required_fields:
                assert field in activity_details, f"Missing field '{field}' in {activity_name}"
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student(self, client):
        """Test signing up a new student for an activity"""
        # Arrange
        activity_name = "Chess Club"
        new_student_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student_email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert new_student_email in activities[activity_name]["participants"]
    
    def test_signup_duplicate_student(self, client):
        """Test that duplicate signups are rejected"""
        # Arrange
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_student}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for non-existent activity"""
        # Arrange
        nonexistent_activity = "NonExistent Club"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_updates_participant_count(self, client):
        """Test that signup updates the participant list"""
        # Arrange
        activity_name = "Programming Class"
        new_student = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )
        
        # Assert
        final_count = len(activities[activity_name]["participants"])
        assert final_count == initial_count + 1
        assert new_student in activities[activity_name]["participants"]


class TestRemoveParticipant:
    """Tests for POST /activities/{activity_name}/remove endpoint"""
    
    def test_remove_existing_participant(self, client):
        """Test removing a student from an activity"""
        # Arrange
        activity_name = "Chess Club"
        student_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": student_to_remove}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert student_to_remove not in activities[activity_name]["participants"]
    
    def test_remove_nonexistent_participant(self, client):
        """Test removing a student who isn't signed up"""
        # Arrange
        activity_name = "Chess Club"
        not_signed_up_student = "notstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": not_signed_up_student}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_remove_from_nonexistent_activity(self, client):
        """Test removing from non-existent activity"""
        # Arrange
        nonexistent_activity = "NonExistent Club"
        student_email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/remove",
            params={"email": student_email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_updates_participant_count(self, client):
        """Test that removal updates the participant list"""
        # Arrange
        activity_name = "Chess Club"
        student_to_remove = "michael@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])
        
        # Act
        client.post(
            f"/activities/{activity_name}/remove",
            params={"email": student_to_remove}
        )
        
        # Assert
        final_count = len(activities[activity_name]["participants"])
        assert final_count == initial_count - 1
        assert student_to_remove not in activities[activity_name]["participants"]


class TestSignupAndRemoveWorkflow:
    """Integration tests for signup and remove workflows"""
    
    def test_signup_then_remove_workflow(self, client):
        """Test the complete workflow of signing up and removing"""
        # Arrange
        activity_name = "Gym Class"
        test_email = "workflow@mergington.edu"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert - Signup successful
        assert signup_response.status_code == 200
        assert test_email in activities[activity_name]["participants"]
        
        # Act - Remove
        remove_response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": test_email}
        )
        
        # Assert - Removal successful
        assert remove_response.status_code == 200
        assert test_email not in activities[activity_name]["participants"]
    
    def test_signup_remove_signup_workflow(self, client):
        """Test signing up, removing, and signing up again"""
        # Arrange
        activity_name = "Programming Class"
        test_email = "workflow2@mergington.edu"
        
        # Act - First signup
        signup1_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert - First signup successful
        assert signup1_response.status_code == 200
        assert test_email in activities[activity_name]["participants"]
        
        # Act - Remove
        remove_response = client.post(
            f"/activities/{activity_name}/remove",
            params={"email": test_email}
        )
        
        # Assert - Removal successful
        assert remove_response.status_code == 200
        assert test_email not in activities[activity_name]["participants"]
        
        # Act - Second signup
        signup2_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email}
        )
        
        # Assert - Second signup successful
        assert signup2_response.status_code == 200
        assert test_email in activities[activity_name]["participants"]
