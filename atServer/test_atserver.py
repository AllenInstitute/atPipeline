import os
import tempfile
import json
import pytest
from main import app

# Based on http://flask.pocoo.org/docs/1.0/testing/

@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        pass

    yield client

def test_get_version(client):
    rv = client.get('/api/version')
    assert rv.status_code == 200
    assert b"0.1" in rv.data

def test_get_status(client):
    rv = client.get('/api/status')
    assert rv.status_code == 200
    try:
        json.loads(rv.data)
    except Exception as e:
        pytest.fail("Unexpected exception parsing json result: %s" % e)

