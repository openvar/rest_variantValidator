"""Tests for the rate limiting code
Currently limited to just testing that it works and keeps to the requested time.
This code relies on the /hello/limit endpoint and relies on it's 1 access per-
second limit.
"""

# Import necessary packages
import time
import pytest
from flask import g
from rest_VariantValidator.utils.limiter import limiter
from rest_VariantValidator.app import application  # Import your Flask app

pytestmark = pytest.mark.usefixtures("check_object_pool_leaks")

# Fixture to set up the test client
@pytest.fixture(scope='module',name='client')
def rate_limit_test_client():
    """Return a test client that works for rate limiting"""
    application.testing = False
    application.debug = False
    application.config['PROPAGATE_EXCEPTIONS'] = True
    # This is fragile, and previous workarounds have failed before, so may
    # break on updates to the limiter or flask test client code.
    with application.app_context():
        setattr(g, '%s_rate_limiting_complete' % limiter._key_prefix, False)
    test_client = application.test_client()  # Create a test client to interact with the app

    yield test_client  # This is where the tests will run


# Test the limiter works as intended,
def test_limit_endpoint_error_immediate(client):
    """Provoke a limiter error by repeated requests to a limited endpoint"""
    response = client.get('/hello/limit', headers={'Content-Type': 'application/json'})
    response = client.get('/hello/limit', headers={'Content-Type': 'application/json'})
    assert response.status_code == 429
    assert response.json["message"] == "Rate limit hit for this endpoint: See the endpoint documentation at https://rest.variantvalidator.org"

def test_limit_endpoint_error_delayed(client):
    """
    Provoke a limiter error by repeated requests to a limited endpoint,
    but with a partial (sub 1 second) delay.
    """
    response = client.get('/hello/limit', headers={'Content-Type': 'application/json'})
    time.sleep(0.5)
    response = client.get('/hello/limit', headers={'Content-Type': 'application/json'})
    assert response.status_code == 429
    assert response.json["message"] == "Rate limit hit for this endpoint: See the endpoint documentation at https://rest.variantvalidator.org"

def test_limit_endpoint_success(client):
    """Repeat the same as above, but with a 1 second delay to exceed limit"""
    response = client.get('/hello/limit', headers={'Content-Type': 'application/json'})
    time.sleep(1)
    response = client.get('/hello/limit', headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
