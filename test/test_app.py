import sys
import os

# Add the parent directory to sys.path so app.py can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app  # now this will work

def test_home():
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 200