import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
import copy

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app with fresh activities data"""
    # Store original activities
    original_activities = copy.deepcopy(activities)
    
    # Create client
    test_client = TestClient(app)
    
    yield test_client
    
    # Restore original activities after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def sample_activity():
    """Provide a sample activity name for testing"""
    return "Chess Club"


@pytest.fixture
def sample_email():
    """Provide a sample email for testing"""
    return "test@mergington.edu"
