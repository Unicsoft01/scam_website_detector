import pytest

from app.collectors.browser_environment import (
    BrowserObservation,
)

from app.features.behavioural_features import (
    extract_behavioural_features,
)


def test_basic_behavioural_features():
    observation = (
        BrowserObservation(
            submitted_url=(
                "https://example.com"
            ),

            success=True,

            initial_url=(
                "https://example.com/"
            ),

            final_url=(
                "https://example.com/account"
            ),

            request_urls=[
                "https://example.com/",
                "https://example.com/app.js",
                "https://cdn.example.com/a.css",
                "https://thirdparty.com/x.js",
            ],

            redirect_chain=[
                "http://example.com/",
                "https://example.com/",
            ],

            automatic_navigation_urls=[
                "https://example.com/account"
            ],

            popup_count=1,
            dialog_count=2,
            download_count=1,

            dom_mutation_count=12,

            form_action_change_count=1,

            dynamic_form_count=1,

            title_change_count=2,

            countdown_detected=True,

            page_error_count=1,

            failed_requests=[
                "https://example.com/missing.js"
            ],
        )
    )

    features = (
        extract_behavioural_features(
            observation
        )
    )

    assert (
        features[
            "redirect_count"
        ]
        == 1
    )

    assert (
        features[
            "cross_domain_redirect_count"
        ]
        == 0
    )

    assert (
        features[
            "popup_count"
        ]
        == 1
    )

    assert (
        features[
            "dialog_count"
        ]
        == 2
    )

    assert (
        features[
            "automatic_navigation_count"
        ]
        == 1
    )

    assert (
        features[
            "has_automatic_navigation"
        ]
        == 1
    )

    assert (
        features[
            "external_request_count"
        ]
        == 1
    )

    assert (
        features[
            "external_request_ratio"
        ]
        == pytest.approx(
            0.25
        )
    )

    assert (
        features[
            "download_attempt_count"
        ]
        == 1
    )

    assert (
        features[
            "dom_mutation_count"
        ]
        == 12
    )

    assert (
        features[
            "form_action_change_count"
        ]
        == 1
    )

    assert (
        features[
            "dynamic_form_count"
        ]
        == 1
    )

    assert (
        features[
            "title_change_count"
        ]
        == 2
    )

    assert (
        features[
            "countdown_detected"
        ]
        == 1
    )


def test_cross_domain_redirect():
    observation = (
        BrowserObservation(
            submitted_url=(
                "https://example.com"
            ),

            success=True,

            redirect_chain=[
                "https://example.com",
                "https://different-site.com",
                "https://different-site.com/login",
            ],
        )
    )

    features = (
        extract_behavioural_features(
            observation
        )
    )

    assert (
        features[
            "redirect_count"
        ]
        == 2
    )

    assert (
        features[
            "cross_domain_redirect_count"
        ]
        == 1
    )


def test_zero_request_ratio():
    observation = (
        BrowserObservation(
            submitted_url=(
                "https://example.com"
            ),
            success=True,
        )
    )

    features = (
        extract_behavioural_features(
            observation
        )
    )

    assert (
        features[
            "total_request_count"
        ]
        == 0
    )

    assert (
        features[
            "external_request_ratio"
        ]
        == 0.0
    )



# 
def test_state_changing_attempt_count():
    observation = (
        BrowserObservation(
            submitted_url=(
                "https://example.com"
            ),

            success=True,

            blocked_requests=[
                {
                    "url":
                        "https://example.com/api",

                    "method":
                        "POST",

                    "resource_type":
                        "fetch",

                    "reason":
                        "HTTP method blocked",
                },

                {
                    "url":
                        "https://example.com/data",

                    "method":
                        "GET",

                    "resource_type":
                        "fetch",

                    "reason":
                        "Other reason",
                },

                {
                    "url":
                        "https://example.com/delete",

                    "method":
                        "DELETE",

                    "resource_type":
                        "fetch",

                    "reason":
                        "HTTP method blocked",
                },
            ],
        )
    )

    features = (
        extract_behavioural_features(
            observation
        )
    )

    assert (
        features[
            "blocked_request_count"
        ]
        == 3
    )

    assert (
        features[
            "state_changing_request_attempt_count"
        ]
        == 2
    )    