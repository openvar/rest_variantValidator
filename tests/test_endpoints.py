# Import necessary packages
import pytest
from rest_VariantValidator.app import application  # Import your Flask app


# Fixture to set up the test client
@pytest.fixture(scope='module')
def client():
    application.testing = True
    return application.test_client()  # Create a test client to interact with the app


# Test function for the /hello/ endpoint
def test_hello_endpoint(client):
    response = client.get('/hello/')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert response.json["status"] == "hello_world"  # Check the JSON response content
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
