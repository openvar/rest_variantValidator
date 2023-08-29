# Import necessary packages
import pytest
from rest_VariantValidator.app import application  # Import your Flask app


# Fixture to set up the test client
@pytest.fixture(scope='module')
def client():
    application.testing = True
    return application.test_client()  # Create a test client to interact with the app


# Test function for exception handlers
def test_bad_request_url(client):
    response = client.get('/nonexistent/?content-type=application%2Fjson')  # Send GET request to a nonexistent endpoint
    assert response.status_code == 404  # Check if the response status code is 404 NOT FOUND
    assert response.json["message"] == "Requested Endpoint not found"


def test_bad_request_code(client):
    response = client.get('/trigger_error/404')  # Send a GET request to a nonexistent endpoint
    assert response.status_code == 404  # Check if the response status code is 404 NOT FOUND
    assert response.json["message"] == "Requested Endpoint not found"


def test_error_code(client):
    response = client.get('/hello/trigger_error/500')  # Send a GET request to a nonexistent endpoint
    assert response.status_code == 500  # Check if the response status code is 404 NOT FOUND
    assert response.json["message"] == "Internal Server Error"


def test_connection_error(client):
    response = client.get('/hello/trigger_error/999')  # Send a GET request to a nonexistent endpoint
    assert response.status_code == 504  # Check if the response status code is 404 NOT FOUND
    assert response.json["message"] == "https://rest.variantvalidator.org/variantvalidator currently unavailable"
