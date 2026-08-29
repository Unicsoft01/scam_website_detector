from unittest.mock import patch

from app.collectors.dns_collector import (
    collect_dns_information,
)


@patch(
    "app.collectors.dns_collector._resolve_record"
)
def test_dns_collection_with_records(
    mock_resolve
):
    def side_effect(
        domain,
        record_type
    ):
        responses = {
            "A": (
                ["93.184.216.34"],
                None,
            ),
            "AAAA": (
                [],
                "NO_ANSWER",
            ),
            "MX": (
                ["10 mail.example.com."],
                None,
            ),
            "NS": (
                [
                    "ns1.example.com.",
                    "ns2.example.com.",
                ],
                None,
            ),
        }

        return responses[
            record_type
        ]

    mock_resolve.side_effect = (
        side_effect
    )

    result = (
        collect_dns_information(
            "example.com"
        )
    )

    assert result.dns_resolved is True
    assert result.a_count == 1
    assert result.aaaa_count == 0
    assert result.mx_count == 1
    assert result.ns_count == 2


@patch(
    "app.collectors.dns_collector._resolve_record"
)
def test_dns_failure_does_not_crash(
    mock_resolve
):
    mock_resolve.return_value = (
        [],
        "NXDOMAIN",
    )

    result = (
        collect_dns_information(
            "nonexistent.invalid"
        )
    )

    assert result.dns_resolved is False
    assert result.a_count == 0
    assert result.mx_count == 0
    assert result.dns_error is not None