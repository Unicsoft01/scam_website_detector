from unittest.mock import patch

from app.collectors.browser_environment import (
    observe_public_url,
    observe_synthetic_html,
)


@patch(
    "app.collectors.browser_environment."
    "is_public_destination"
)
def test_unsafe_initial_destination(
    mock_public,
):
    mock_public.return_value = (
        False,
        "Private destination blocked",
    )

    result = (
        observe_public_url(
            "http://127.0.0.1"
        )
    )

    assert (
        result.success
        is False
    )

    assert (
        result.error_type
        == "unsafe_destination"
    )


def test_synthetic_html_loads():
    result = (
        observe_synthetic_html(
            """
            <html>
                <body>
                    Safe test
                </body>
            </html>
            """
        )
    )

    assert (
        result.success
        is True
    )


def test_synthetic_dialog_is_handled():
    result = (
        observe_synthetic_html(
            """
            <html>
                <body>
                    Dialog test
                </body>
            </html>
            """,

            javascript="""
            () => {
                setTimeout(
                    () => alert("test"),
                    50
                );
            }
            """,

            observation_time_ms=500,
        )
    )

    assert (
        result.success
        is True
    )

    assert (
        result.dialog_count
        >= 1
    )


def test_synthetic_popup_is_handled():
    result = (
        observe_synthetic_html(
            """
            <html>
                <body>
                    Popup test
                </body>
            </html>
            """,

            javascript="""
            () => {
                window.open(
                    "about:blank",
                    "_blank"
                );
            }
            """,

            observation_time_ms=500,
        )
    )

    assert (
        result.success
        is True
    )

    assert (
        result.popup_count
        >= 1
    )