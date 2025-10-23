from flask.testing import FlaskClient
from werkzeug.test import TestResponse


def test_health(client: FlaskClient):

    res: TestResponse = client.get("/health")

    # Assert
    assert res.status_code == 200
    assert res.is_json
    assert res.get_json() == {"status": "ok"}
