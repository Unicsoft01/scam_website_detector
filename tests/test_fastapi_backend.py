from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(
    app
)


def test_home():

    response = client.get(
        "/"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        data["status"]
        == "running"
    )


def test_api_information():

    response = client.get(
        "/api"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        "submit_scan"
        in data["endpoints"]
    )


def test_missing_scan_returns_404():

    response = client.get(
        "/api/scans/999999999"
    )

    assert (
        response.status_code
        == 404
    )


def test_invalid_scan_id_type():

    response = client.get(
        "/api/scans/not-an-integer"
    )

    assert (
        response.status_code
        == 422
    )


def test_invalid_scan_id_value():

    response = client.get(
        "/api/scans/0"
    )

    assert (
        response.status_code
        == 400
    )


def test_invalid_scan_request():

    response = client.post(
        "/api/scans",
        json={
            "url": ""
        },
    )

    assert (
        response.status_code
        == 422
    )


def test_missing_url_request():

    response = client.post(
        "/api/scans",
        json={},
    )

    assert (
        response.status_code
        == 422
    )


def test_scan_history():

    response = client.get(
        "/api/scans"
    )

    assert (
        response.status_code
        == 200
    )

    data = response.json()

    assert (
        "total"
        in data
    )

    assert (
        "scans"
        in data
    )


def test_history_limit_validation():

    response = client.get(
        "/api/scans?limit=101"
    )

    assert (
        response.status_code
        == 422
    )



# 
def test_valid_scan_request_runtime_unavailable():

    response = client.post(
        "/api/scans",
        json={
            "url":
                "https://example.com"
        },
    )

    assert (
        response.status_code
        == 503
    )

    data = response.json()

    assert (
        data["error"]
        == "http_error"
    )

    assert (
        "scan runtime"
        in data["message"].lower()
    )    