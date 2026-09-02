from app.core.failures import (
    FailureCode,
    ScanState,
)

from app.services.failure_service import (
    FailureService,
)


def test_invalid_url_is_failed():

    failure = (
        FailureService.invalid_url()
    )

    assert (
        failure.state
        == ScanState.FAILED
    )

    assert (
        failure.code
        == FailureCode.INVALID_URL
    )


def test_private_destination_is_failed():

    failure = (
        FailureService
        .blocked_private_destination()
    )

    assert (
        failure.state
        == ScanState.FAILED
    )


def test_dns_failure_is_failed():

    failure = (
        FailureService.dns_failure()
    )

    assert (
        failure.state
        == ScanState.FAILED
    )


def test_connection_timeout_is_failed():

    failure = (
        FailureService
        .connection_timeout()
    )

    assert (
        failure.state
        == ScanState.FAILED
    )


def test_inaccessible_site_is_failed():

    failure = (
        FailureService
        .inaccessible_site()
    )

    assert (
        failure.state
        == ScanState.FAILED
    )


def test_tls_failure_is_failed():

    failure = (
        FailureService.tls_failure()
    )

    assert (
        failure.state
        == ScanState.FAILED
    )


def test_non_html_is_failed():

    failure = (
        FailureService
        .non_html_content()
    )

    assert (
        failure.state
        == ScanState.FAILED
    )


def test_browser_timeout_is_partial():

    failure = (
        FailureService.browser_timeout()
    )

    assert (
        failure.state
        == ScanState.PARTIAL
    )

    assert (
        failure.behavioural_available
        is False
    )


def test_behavioural_unavailable_is_partial():

    failure = (
        FailureService
        .behavioural_unavailable()
    )

    assert (
        failure.state
        == ScanState.PARTIAL
    )

    assert (
        failure.behavioural_available
        is False
    )


def test_internal_error_is_failed():

    failure = (
        FailureService.internal_error()
    )

    assert (
        failure.state
        == ScanState.FAILED
    )


def test_failed_analysis_is_not_completed():

    failure = (
        FailureService.dns_failure()
    )

    assert (
        failure.state
        != ScanState.COMPLETED
    )