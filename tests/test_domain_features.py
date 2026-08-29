from unittest.mock import patch

from app.collectors.dns_collector import (
    DNSResult,
)
from app.collectors.rdap_collector import (
    RDAPResult,
)
from app.features.domain_features import (
    extract_domain_dns_features,
    get_domain_structure,
)


def test_domain_structure():
    result = get_domain_structure(
        "https://login.secure.example.co.uk/path"
    )

    assert (
        result["subdomain"]
        == "login.secure"
    )

    assert (
        result["domain"]
        == "example"
    )

    assert (
        result["suffix"]
        == "co.uk"
    )

    assert (
        result["registrable_domain"]
        == "example.co.uk"
    )

    assert (
        result["subdomain_count"]
        == 2
    )


def test_ip_hostname_structure():
    result = get_domain_structure(
        "http://192.0.2.10/test"
    )

    assert (
        result["is_ip_hostname"]
        == 1
    )

    assert (
        result["registrable_domain"]
        == "192.0.2.10"
    )


@patch(
    "app.features.domain_features.collect_dns_information"
)
@patch(
    "app.features.domain_features.collect_rdap_information"
)
def test_combined_domain_features(
    mock_rdap,
    mock_dns,
):
    mock_dns.return_value = DNSResult(
        domain="example.com",
        dns_resolved=True,

        a_records=[
            "93.184.216.34"
        ],

        aaaa_records=[],

        mx_records=[
            "10 mail.example.com."
        ],

        ns_records=[
            "ns1.example.com."
        ],

        a_count=1,
        aaaa_count=0,
        mx_count=1,
        ns_count=1,

        dns_error=None,
    )

    mock_rdap.return_value = RDAPResult(
        domain="example.com",
        rdap_available=True,

        registration_date=(
            "2020-01-01T00:00:00Z"
        ),

        expiration_date=None,
        last_changed_date=None,

        domain_age_days=2000,

        rdap_error=None,
    )

    features = (
        extract_domain_dns_features(
            "https://www.example.com"
        )
    )

    assert (
        features["dns_resolved"]
        == 1
    )

    assert (
        features["has_a_record"]
        == 1
    )

    assert (
        features["has_mx_record"]
        == 1
    )

    assert (
        features["rdap_available"]
        == 1
    )

    assert (
        features["domain_age_days"]
        == 2000
    )