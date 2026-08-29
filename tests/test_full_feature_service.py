from unittest.mock import patch

from app.services.full_feature_service import (
    extract_full_features,
)


@patch(
    "app.services.full_feature_service."
    "build_heuristic_observation"
)
@patch(
    "app.services.full_feature_service."
    "build_behavioural_observation"
)
def test_full_success(
    mock_behavioural,
    mock_heuristic,
):

    mock_heuristic.return_value = {
        "success": True,

        "features": {
            "url_length": 20,
            "dns_resolved": 1,
            "form_count": 1,
        },

        "metadata": {
            "html_available": True,
        },
    }

    mock_behavioural.return_value = {
        "success": True,

        "features": {
            "popup_count": 0,
            "dialog_count": 0,
            "dom_mutation_count": 4,
        },

        "metadata": {},
    }

    result = (
        extract_full_features(
            "https://example.com"
        )
    )

    assert (
        result.heuristic_success
        is True
    )

    assert (
        result.heuristic_complete
        is True
    )

    assert (
        result.behavioural_success
        is True
    )

    assert (
        result.hybrid_success
        is True
    )


@patch(
    "app.services.full_feature_service."
    "build_heuristic_observation"
)
@patch(
    "app.services.full_feature_service."
    "build_behavioural_observation"
)
def test_missing_html_blocks_hybrid(
    mock_behavioural,
    mock_heuristic,
):

    mock_heuristic.return_value = {
        "success": True,

        "features": {
            "url_length": 20,
        },

        "metadata": {
            "html_available": False,
        },
    }

    mock_behavioural.return_value = {
        "success": True,

        "features": {
            "popup_count": 0,
        },

        "metadata": {},
    }

    result = (
        extract_full_features(
            "https://example.com"
        )
    )

    assert (
        result.heuristic_success
        is True
    )

    assert (
        result.heuristic_complete
        is False
    )

    assert (
        result.behavioural_success
        is True
    )

    assert (
        result.hybrid_success
        is False
    )


@patch(
    "app.services.full_feature_service."
    "build_heuristic_observation"
)
@patch(
    "app.services.full_feature_service."
    "build_behavioural_observation"
)
def test_behavioural_failure_blocks_hybrid(
    mock_behavioural,
    mock_heuristic,
):

    mock_heuristic.return_value = {
        "success": True,

        "features": {
            "url_length": 20,
        },

        "metadata": {
            "html_available": True,
        },
    }

    mock_behavioural.return_value = {
        "success": False,

        "features": None,

        "metadata": {
            "error_type":
                "TimeoutError",

            "error_message":
                "Navigation timed out",
        },
    }

    result = (
        extract_full_features(
            "https://example.com"
        )
    )

    assert (
        result.heuristic_complete
        is True
    )

    assert (
        result.behavioural_success
        is False
    )

    assert (
        result.hybrid_success
        is False
    )


@patch(
    "app.services.full_feature_service."
    "build_heuristic_observation"
)
@patch(
    "app.services.full_feature_service."
    "build_behavioural_observation"
)
def test_string_feature_is_rejected(
    mock_behavioural,
    mock_heuristic,
):

    mock_heuristic.return_value = {
        "success": True,

        "features": {
            "url_length": 20,

            "certificate_issuer":
                "Some Certificate Authority",
        },

        "metadata": {
            "html_available": True,
        },
    }

    mock_behavioural.return_value = {
        "success": True,

        "features": {
            "popup_count": 0,
        },

        "metadata": {},
    }

    result = (
        extract_full_features(
            "https://example.com"
        )
    )

    assert (
        result.heuristic_success
        is False
    )

    assert (
        result.hybrid_success
        is False
    )

    assert (
        result.heuristic_error
        is not None
    )