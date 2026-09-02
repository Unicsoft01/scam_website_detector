from app.services.explanation_service import (
    ExplanationService,
)


def test_external_form_indicator():

    service = ExplanationService()

    indicators = service.explain(
        heuristic_features={
            "h_external_form_action": 1,
        },
        behavioural_features=None,
    )

    titles = [
        item.title
        for item in indicators
    ]

    assert (
        "External form action detected"
        in titles
    )


def test_cross_domain_redirect_indicator():

    service = ExplanationService()

    indicators = service.explain(
        heuristic_features=None,
        behavioural_features={
            "b_cross_domain_redirect_count": 3,
        },
    )

    titles = [
        item.title
        for item in indicators
    ]

    assert (
        "Multiple cross-domain redirects observed"
        in titles
    )


def test_popup_indicator():

    service = ExplanationService()

    indicators = service.explain(
        heuristic_features=None,
        behavioural_features={
            "b_popup_count": 2,
        },
    )

    titles = [
        item.title
        for item in indicators
    ]

    assert (
        "JavaScript popup activity observed"
        in titles
    )


def test_domain_information_unavailable():

    service = ExplanationService()

    indicators = service.explain(
        heuristic_features={
            "h_domain_age_days": None,
        },
        behavioural_features=None,
    )

    titles = [
        item.title
        for item in indicators
    ]

    assert (
        (
            "Domain registration "
            "information unavailable"
        )
        in titles
    )


def test_zero_popup_not_reported():

    service = ExplanationService()

    indicators = service.explain(
        heuristic_features=None,
        behavioural_features={
            "b_popup_count": 0,
        },
    )

    titles = [
        item.title
        for item in indicators
    ]

    assert (
        "JavaScript popup activity observed"
        not in titles
    )


def test_one_redirect_is_not_multiple():

    service = ExplanationService()

    indicators = service.explain(
        heuristic_features=None,
        behavioural_features={
            "b_cross_domain_redirect_count": 1,
        },
    )

    titles = [
        item.title
        for item in indicators
    ]

    assert (
        "Cross-domain redirect observed"
        in titles
    )

    assert (
        "Multiple cross-domain redirects observed"
        not in titles
    )


def test_high_severity_first():

    service = ExplanationService()

    indicators = service.explain(
        heuristic_features={
            "h_external_form_action": 1,
            "h_url_length": 150,
        },
        behavioural_features=None,
    )

    assert (
        indicators[0].severity
        == "high"
    )


def test_maximum_indicator_limit():

    service = ExplanationService()

    indicators = service.explain(
        heuristic_features={
            "h_external_form_action": 1,
            "h_password_field": 1,
            "h_url_length": 150,
            "h_subdomain_count": 4,
            "h_tls_available": 0,
        },
        behavioural_features={
            "b_popup_count": 2,
            "b_dialog_count": 1,
            "b_download_attempt_count": 1,
            "b_cross_domain_redirect_count": 3,
            "b_automatic_navigation_count": 2,
        },
        max_indicators=5,
    )

    assert len(indicators) == 5