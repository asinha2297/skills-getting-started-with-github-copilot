import pytest
from fastapi.testclient import TestClient
from src.app import app

# Create a TestClient instance for testing
client = TestClient(app)

def test_get_activities():
    """Test GET /activities endpoint returns activity data"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    
    # Check structure of first activity
    activity = list(data.values())[0]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_success():
    """Test successful signup for an activity"""
    response = client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "Signed up" in data["message"]
    
    # Verify the student was added
    response = client.get("/activities")
    activities = response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    """Test that duplicate signup is prevented"""
    # First signup
    client.post("/activities/Programming%20Class/signup?email=dup@mergington.edu")
    
    # Second signup should fail
    response = client.post("/activities/Programming%20Class/signup?email=dup@mergington.edu")
    assert response.status_code == 400
    
    data = response.json()
    assert "already signed up" in data["detail"]

def test_signup_invalid_activity():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test@mergington.edu")
    assert response.status_code == 404
    
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_delete_success():
    """Test successful participant removal"""
    # First add a participant
    client.post("/activities/Gym%20Class/signup?email=deleteme@mergington.edu")
    
    # Then delete them
    response = client.delete("/activities/Gym%20Class/signup?email=deleteme@mergington.edu")
    assert response.status_code == 200
    
    data = response.json()
    assert "Unregistered" in data["message"]
    
    # Verify they were removed
    response = client.get("/activities")
    activities = response.json()
    assert "deleteme@mergington.edu" not in activities["Gym Class"]["participants"]

def test_delete_not_found():
    """Test deletion of non-existent participant"""
    response = client.delete("/activities/Chess%20Club/signup?email=notexist@mergington.edu")
    assert response.status_code == 404
    
    data = response.json()
    assert "Participant not found" in data["detail"]