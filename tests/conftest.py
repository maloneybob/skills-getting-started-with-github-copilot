import pytest
import sys
import os

# Add src directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    """Fixture for FastAPI test client"""
    return TestClient(app)
