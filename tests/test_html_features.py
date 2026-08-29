import pytest

from app.features.html_features import (
    extract_html_features,
)


def test_form_and_password_features():
    html = """
    <html>
        <body>
            <form action="/login">
                <input
                    type="text"
                    name="username"
                >

                <input
                    type="password"
                    name="password"
                >

                <input
                    type="hidden"
                    name="token"
                    value="123"
                >
            </form>
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features["form_count"]
        == 1
    )

    assert (
        features[
            "password_field_count"
        ]
        == 1
    )

    assert (
        features[
            "hidden_input_count"
        ]
        == 1
    )

    assert (
        features[
            "has_password_field"
        ]
        == 1
    )


def test_payment_fields():
    html = """
    <html>
        <body>
            <form>
                <input
                    name="card_number"
                >

                <input
                    name="cvv"
                >

                <input
                    id="billing_address"
                >
            </form>
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://shop.example.com",
            html,
        )
    )

    assert (
        features[
            "payment_field_count"
        ]
        >= 2
    )

    assert (
        features[
            "has_payment_field"
        ]
        == 1
    )


def test_iframe_and_script_counts():
    html = """
    <html>
        <body>
            <iframe src="/frame"></iframe>

            <script src="/one.js"></script>
            <script>
                console.log("test");
            </script>
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features["iframe_count"]
        == 1
    )

    assert (
        features["script_count"]
        == 2
    )

    assert (
        features["has_iframe"]
        == 1
    )


def test_internal_and_external_links():
    html = """
    <html>
        <body>
            <a href="/about">
                About
            </a>

            <a href="https://support.example.com/help">
                Support
            </a>

            <a href="https://different-site.com">
                External
            </a>
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://www.example.com",
            html,
        )
    )

    assert (
        features[
            "internal_link_count"
        ]
        == 2
    )

    assert (
        features[
            "external_link_count"
        ]
        == 1
    )

    assert (
        features[
            "external_link_ratio"
        ]
        == pytest.approx(
            1 / 3,
            rel=1e-5,
        )
    )


def test_external_form_action():
    html = """
    <html>
        <body>
            <form
                action="https://different-site.com/submit"
            >
                <input
                    type="password"
                >
            </form>
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features[
            "external_form_action_count"
        ]
        == 1
    )

    assert (
        features[
            "has_external_form_action"
        ]
        == 1
    )

    assert (
        features[
            "suspicious_form_action_count"
        ]
        >= 1
    )


def test_relative_form_action_is_internal():
    html = """
    <form action="/account/login">
        <input type="password">
    </form>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features[
            "external_form_action_count"
        ]
        == 0
    )


def test_javascript_form_action():
    html = """
    <form action="javascript:void(0)">
        <input name="username">
    </form>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features[
            "javascript_form_action_count"
        ]
        == 1
    )

    assert (
        features[
            "suspicious_form_action_count"
        ]
        == 1
    )


def test_hidden_elements():
    html = """
    <html>
        <body>
            <div hidden>
                Secret
            </div>

            <p style="display:none">
                Hidden
            </p>

            <span aria-hidden="true">
                Hidden
            </span>
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features[
            "hidden_element_count"
        ]
        >= 3
    )


def test_meta_refresh():
    html = """
    <html>
        <head>
            <meta
                http-equiv="refresh"
                content="5; url=https://example.com/next"
            >
        </head>

        <body>
            Test
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features[
            "meta_refresh_count"
        ]
        == 1
    )

    assert (
        features[
            "has_meta_refresh"
        ]
        == 1
    )


def test_login_language():
    html = """
    <html>
        <body>
            Please sign in to verify account.
            Enter your username and password.
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features[
            "login_keyword_count"
        ]
        >= 3
    )


def test_payment_language():
    html = """
    <html>
        <body>
            Complete payment using
            your credit card.
            Enter your card number
            and CVV.
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features[
            "payment_keyword_count"
        ]
        >= 2
    )


def test_crypto_language():
    html = """
    <html>
        <body>
            Send Bitcoin to this
            crypto wallet address.
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features[
            "crypto_keyword_count"
        ]
        >= 2
    )


def test_urgency_language():
    html = """
    <html>
        <body>
            URGENT:
            verify now.
            Your account is locked.
            Act now.
        </body>
    </html>
    """

    features = (
        extract_html_features(
            "https://example.com",
            html,
        )
    )

    assert (
        features[
            "urgency_keyword_count"
        ]
        >= 2
    )


def test_empty_html_does_not_crash():
    features = (
        extract_html_features(
            "https://example.com",
            ""
        )
    )

    assert (
        features["form_count"]
        == 0
    )

    assert (
        features["link_count"]
        == 0
    )

    assert (
        features[
            "external_link_ratio"
        ]
        == 0.0
    )