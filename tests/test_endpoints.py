
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
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response


def test_lovd_endpoint(client):
    response = client.get('/LOVD/lovd/GRCh38/17-50198002-C-A/all/mane/True/False?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response


def test_vf_endpoint(client):
    response = client.get('/VariantFormatter/variantformatter/GRCh38/NC_000017.10%3Ag.48275363C%3EA/all/mane/True?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response


def test_vv_endpoint(client):
    response = client.get('/VariantValidator/variantvalidator/GRCh38/NM_000088.3%3Ac.589G%3ET/mane?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response


def test_g2t_endpoint(client):
    response = client.get('/VariantValidator/tools/gene2transcripts/COL1A1?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK


def test_g2t2_endpoint(client):
    response = client.get('/VariantValidator/tools/gene2transcripts_v2/COL1A1%7CCOL1A2%7CCOL5A1/mane/all/GRCh38?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK


def test_h2ref_endpoint(client):
    response = client.get('/VariantValidator/tools/hgvs2reference/NM_000088.3%3Ac.589G%3ET?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK

