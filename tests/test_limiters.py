"""Tests for the usage limiting code, for both rate and concurrency
Currently rate limit code is limited to just testing that it works and keeps to
the requested time.
This code relies on the /hello/limit endpoint and relies on it's 1 access per-
second limit to test the rate limiting code, and the /hello/limit_concurrent test
to test the concurrency limit.
"""

# Import necessary packages
import time
import threading
import pytest
from flask import g
from rest_VariantValidator.utils.limiter import limiter
from rest_VariantValidator.app import application  # Import your Flask app

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

# Test the concurrency limiter
# This set of tests use threading so timings are not 100%. The limit_concurrent
# endpoint takes 2 seconds to run, when it works, unsuccessful attempts due to
# concurrency will count towards the rate limit, but rate limit failures do not.
def test_concurrency_limit_endpoint_error_immediate(client):
    """Test that immediate repeated requests provoke the normal rate limit first"""
    def test_concurrent(client):
        response = client.get('/hello/limit_concurrent', headers={'Content-Type': 'application/json'})
    thread = threading.Thread(target=test_concurrent, args=(client,))
    thread.start()
    time.sleep(0.1)
    response = client.get('/hello/limit_concurrent', headers={'Content-Type': 'application/json'})
    assert response.status_code == 429
    assert response.json["message"] == "Rate limit hit for this endpoint: See the endpoint documentation at https://rest.variantvalidator.org"
    thread.join()
    time.sleep(0.9)

def test_concurrency_limit_endpoint_error_delayed_small(client):
    """
    Provoke a concurrency limiter error by repeated requests to a limited endpoint,
    with a delay long enough to pass the input rate limit.
    """
    def test_concurrent(client):
        print("testing")
        response = client.get('/hello/limit_concurrent', headers={'Content-Type': 'application/json'})
    thread = threading.Thread(target=test_concurrent, args=(client,))
    thread.start()
    time.sleep(1.1)
    response = client.get('/hello/limit_concurrent', headers={'Content-Type': 'application/json'})
    assert response.status_code == 429
    assert response.json["message"].startswith('Concurrency limit exceeded. ')
    thread.join()
    time.sleep(1)

def test_concurrency_limit_endpoint_error_delayed_long(client):
    """
    Provoke a concurrency limiter error by repeated requests to a limited endpoint,
    with a longer delay, long enough to pass the input rate limit and nearly pass the
    concurrency limit for the 2s sleeping test endpoint.
    """
    def test_concurrent(client):
        print("testing")
        response = client.get('/hello/limit_concurrent', headers={'Content-Type': 'application/json'})
    thread = threading.Thread(target=test_concurrent, args=(client,))
    thread.start()
    time.sleep(1.9)
    response = client.get('/hello/limit_concurrent', headers={'Content-Type': 'application/json'})
    assert response.status_code == 429
    assert response.json["message"].startswith('Concurrency limit exceeded. ')
    thread.join()
    time.sleep(1)

def test_concurrency_limit_endpoint_success(client):
    """
    Repeat the same as above, but with a 5 second delay to allow return and exceed
    the concurrency limit
    """
    def test_concurrent(client):
        print("testing")
        response = client.get('/hello/limit_concurrent', headers={'Content-Type': 'application/json'})
    thread = threading.Thread(target=test_concurrent, args=(client,))
    thread.start()
    time.sleep(2.1)
    response = client.get('/hello/limit_concurrent', headers={'Content-Type': 'application/json'})
    assert response.status_code == 200
    thread.join()
    time.sleep(1)
