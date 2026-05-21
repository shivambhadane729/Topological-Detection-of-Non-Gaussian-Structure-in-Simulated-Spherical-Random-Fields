"""Pytest configuration and fixtures."""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_patch():
    import numpy as np
    np.random.seed(42)
    return np.random.normal(0, 1e-5, (64, 64))
