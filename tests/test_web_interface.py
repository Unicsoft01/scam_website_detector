from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(
    app
)


def test_home_page():

    response = client.get(
        "/"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        "text/html"
        in response.headers[
            "content-type"
        ]
    )

    assert (
        "Analyse Website"
        in response.text
    )


def test_home_contains_url_input():

    response = client.get(
        "/"
    )

    assert (
        'id="urlInput"'
        in response.text
    )

    assert (
        'id="scanForm"'
        in response.text
    )


def test_home_loads_scan_javascript():

    response = client.get(
        "/"
    )

    assert (
        "/static/js/scan.js"
        in response.text
    )


def test_history_page():

    response = client.get(
        "/history"
    )

    assert (
        response.status_code
        == 200
    )

    assert (
        "Scan History"
        in response.text
    )


def test_missing_result_page():

    response = client.get(
        "/results/999999999"
    )

    assert (
        response.status_code
        == 404
    )

    assert (
        "Scan Not Found"
        in response.text
    )


def test_static_css_available():

    response = client.get(
        "/static/css/app.css"
    )

    assert (
        response.status_code
        == 200
    )


def test_static_javascript_available():

    response = client.get(
        "/static/js/scan.js"
    )

    assert (
        response.status_code
        == 200
    )