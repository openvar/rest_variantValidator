# Import necessary packages
import pytest
from rest_VariantValidator.app import application  # Import your Flask app

pytestmark = pytest.mark.usefixtures("check_object_pool_leaks")

# Fixture to set up the test client
@pytest.fixture(scope='module')
def client():
    application.testing = False
    application.debug = False
    application.config['PROPAGATE_EXCEPTIONS'] = True
    return application.test_client()  # Create a test client to interact with the app


# Test function for exception handlers
def test_bad_request_url(client):
    response = client.get('/nonexistent/', headers={'Content-Type': 'application/json'})
    assert response.status_code == 404  # Check if the response status code is 404 NOT FOUND
    assert response.json["message"] == "Requested Endpoint not found: See the documentation at https://rest.variantvalidator.org"


def test_bad_request_code(client):
    response = client.get('/trigger_error/404', headers={'Content-Type': 'application/json'})
    assert response.status_code == 404  # Check if the response status code is 404 NOT FOUND
    assert response.json["message"] == "Requested Endpoint not found: See the documentation at https://rest.variantvalidator.org"


def test_error_code(client):
    response = client.get('/hello/trigger_error/500', headers={'Content-Type': 'application/json'})
    assert response.status_code == 500
    assert response.json["message"] == "Unhandled error: contact https://variantvalidator.org/contact_admin/"


def test_limit_code(client):
    response = client.get('/hello/trigger_error/429', headers={'Content-Type': 'application/json'})
    assert response.status_code == 429
    assert response.json["message"] == "Rate limit hit for this endpoint: See the endpoint documentation at https://rest.variantvalidator.org"


def test_connection_error(client):
    response = client.get('/hello/trigger_error/999', headers={'Content-Type': 'application/json'})  # Send a GET request to a nonexistent endpoint
    assert response.status_code == 504  # Check if the response status code is 404 NOT FOUND
    assert response.json["message"] == "https://rest.variantvalidator.org/variantvalidator currently unavailable"
