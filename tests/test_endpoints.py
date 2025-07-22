# Import necessary packages
import pytest
import time
from rest_VariantValidator.app import application  # Import your Flask app


# Fixture to set up the test client
@pytest.fixture(scope='module')
def client():
    application.testing = True
    test_client = application.test_client()  # Create a test client to interact with the app

    yield test_client  # This is where the tests will run


# Test function for the /hello/ endpoint
def test_hello_endpoint(client):
    response = client.get('/hello/')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    time.sleep(1)



def test_lovd_endpoint(client):
    response = client.get('/LOVD/lovd/GRCh38/17-50198002-C-A/all/mane/True/False?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    assert "17-50198002-C-A" in response.json.keys()
    time.sleep(1)

def test_lovd_endpoint_multi(client):
    response = client.get('/LOVD/lovd/GRCh38/17-50198002-C-A|17-50198002-C-T/all/mane/True/False?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    assert "17-50198002-C-A" in response.json.keys()
    assert "17-50198002-C-T" in response.json.keys()
    time.sleep(1)


def test_vf_endpoint(client):
    response = client.get('/VariantFormatter/variantformatter/GRCh38/NC_000017.10%3Ag.48275363C%3EA/all/mane/True?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    time.sleep(1)


def test_vv_endpoint(client):
    response = client.get('/VariantValidator/variantvalidator/GRCh38/NM_000088.3%3Ac.589G%3ET/all?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    assert "NM_000088.3:c.589G>T" in response.json.keys()
    time.sleep(1)


def test_vv_endpoint_multi(client):
    response = client.get('/VariantValidator/variantvalidator/GRCh38/NM_000088.3%3Ac.589G%3ET|NM_000088.3%3Ac.589G%3EA/mane?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    assert "NM_000088.3:c.589G>T" in response.json.keys()
    assert "NM_000088.3:c.589G>A" in response.json.keys()
    time.sleep(1)


def test_g2t_endpoint(client):
    response = client.get('/VariantValidator/tools/gene2transcripts/COL1A1?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert len(response.json) == 8
    time.sleep(1)


def test_g2t2_endpoint(client):
    response = client.get('/VariantValidator/tools/gene2transcripts_v2/COL1A1%7CCOL1A2%7CCOL5A1/mane/all/GRCh38?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert len(response.json) == 3
    time.sleep(1)


def test_h2ref_endpoint(client):
    response = client.get('/VariantValidator/tools/hgvs2reference/NM_000088.3%3Ac.589G%3ET?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    time.sleep(1)


def test_vv_endpoint_all_tx(client):
    response = client.get('/VariantValidator/variantvalidator/GRCh38/NM_000088.3%3Ac.589G%3ET/all?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    time.sleep(1)


def test_vv_endpoint_all_vcf(client):
    response = client.get('/VariantValidator/variantvalidator/GRCh38/17-50198002-C-A/all?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 404  # Check if the response status code is 200 OK
    assert "metadata" not in response.json.keys()  # Check if "metadata" key is in the JSON response
    time.sleep(1)


def test_vv_endpoint_all_genomic(client):
    response = client.get('/VariantValidator/variantvalidator/GRCh38/NC_000017.10:g.48275363C>A/all?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 404  # Check if the response status code is 200 OK
    assert "metadata" not in response.json.keys()  # Check if "metadata" key is in the JSON response
    time.sleep(1)


def test_vv_endpoint_mane_genomic(client):
    response = client.get('/VariantValidator/variantvalidator/GRCh38/NC_000017.10:g.48275363C>A/mane?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    time.sleep(1)


def test_vv_endpoint_mane_vcf(client):
    response = client.get('/VariantValidator/variantvalidator/GRCh38/17-50198002-C-A/mane?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    time.sleep(1)


def test_vv_endpoint_auth_raw_vcf(client):
    response = client.get('/VariantValidator/variantvalidator/GRCh38/17-50198002-C-A/auth_all?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    time.sleep(1)


def test_vv_endpoint_auth_all_vcf(client):
    response = client.get('/VariantValidator/variantvalidator/GRCh38/17-50198002-C-A/auth_raw?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    time.sleep(1)


def test_vv_g2tv2(client):
    response = client.get('/VariantValidator/tools/gene2transcripts_v2/AMPD1/mane/refseq/GRCh38?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert len(response.json) == 1
    time.sleep(1)

def test_lovd_endpoint_all(client):
    response = client.get('/LOVD/lovd/GRCh37/1%3A43815009%3AG%3AT/refseq/all/False/True?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    assert "1:43815009:G:T" in response.json.keys()
    time.sleep(1)


def test_lovd_endpoint_raw(client):
    response = client.get('/LOVD/lovd/GRCh37/1%3A43815009%3AG%3AT/refseq/raw/False/True?content-type=application%2Fjson')  # Send a GET request to the /hello/ endpoint
    assert response.status_code == 200  # Check if the response status code is 200 OK
    assert "metadata" in response.json.keys()  # Check if "metadata" key is in the JSON response
    assert "1:43815009:G:T" in response.json.keys()
    time.sleep(1)
