import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_root_endpoint(client):
    """Test the root endpoint returns Hello World!"""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Hello World!" in rv.data
