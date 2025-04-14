from rest_VariantValidator.wsgi import app
import pytest

pytestmark = pytest.mark.usefixtures("check_object_pool_leaks")

@pytest.fixture(scope='module')
def client():
    app.testing = True
    return app.test_client()  # Create a test client to interact with the app


# Test function for the /hello/ endpoint
def test_wsgi_gateway(client):
    response = client.get('/hello/')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert response.json["status"] == "hello_world"  # Check the JSON response content
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
