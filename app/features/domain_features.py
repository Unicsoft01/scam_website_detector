import ipaddress
from urllib.parse import urlsplit

import tldextract

from app.collectors.dns_collector import (
    collect_dns_information,
)
from app.collectors.rdap_collector import (
    collect_rdap_information,
)
from app.core.url_security import (
    normalize_url,
)


DOMAIN_EXTRACTOR = tldextract.TLDExtract(
    suffix_list_urls=()
)


def get_domain_structure(
    url: str
) -> dict:
    normalized = normalize_url(
        url
    )

    if normalized is None:
        raise ValueError(
            "URL must be a valid HTTP or HTTPS URL."
        )

    parsed = urlsplit(
        normalized
    )

    hostname = (
        parsed.hostname
        or ""
    ).lower()

    try:
        ipaddress.ip_address(
            hostname
        )

        return {
            "hostname": hostname,
            "subdomain": "",
            "domain": hostname,
            "suffix": "",
            "registrable_domain": hostname,
            "subdomain_count": 0,
            "is_ip_hostname": 1,
        }

    except ValueError:
        pass

    extracted = DOMAIN_EXTRACTOR(
        hostname
    )

    subdomain = (
        extracted.subdomain
        or ""
    )

    domain = (
        extracted.domain
        or ""
    )

    suffix = (
        extracted.suffix
        or ""
    )

    if domain and suffix:
        registrable_domain = (
            f"{domain}.{suffix}"
        )
    else:
        registrable_domain = hostname

    subdomain_count = (
        len(
            [
                part
                for part
                in subdomain.split(".")
                if part
            ]
        )
        if subdomain
        else 0
    )

    return {
        "hostname": hostname,
        "subdomain": subdomain,
        "domain": domain,
        "suffix": suffix,
        "registrable_domain": registrable_domain,
        "subdomain_count": subdomain_count,
        "is_ip_hostname": 0,
    }


def extract_domain_dns_features(
    url: str,
    include_rdap: bool = True,
) -> dict:
    """
    Extract domain, DNS and optional RDAP features.

    The function returns structured missing values instead of crashing.
    """

    structure = (
        get_domain_structure(
            url
        )
    )

    domain = structure[
        "registrable_domain"
    ]

    if structure[
        "is_ip_hostname"
    ] == 1:
        return {
            **structure,

            "dns_resolved": 0,
            "a_count": 0,
            "aaaa_count": 0,
            "mx_count": 0,
            "ns_count": 0,

            "has_a_record": 0,
            "has_aaaa_record": 0,
            "has_mx_record": 0,
            "has_ns_record": 0,

            "rdap_available": 0,
            "domain_age_days": None,

            "dns_error": (
                "IP literal hostname"
            ),

            "rdap_error": (
                "RDAP not applicable to IP literal"
            ),
        }

    dns_result = (
        collect_dns_information(
            domain
        )
    )

    features = {
        **structure,

        "dns_resolved": int(
            dns_result.dns_resolved
        ),

        "a_count": (
            dns_result.a_count
        ),

        "aaaa_count": (
            dns_result.aaaa_count
        ),

        "mx_count": (
            dns_result.mx_count
        ),

        "ns_count": (
            dns_result.ns_count
        ),

        "has_a_record": int(
            dns_result.a_count > 0
        ),

        "has_aaaa_record": int(
            dns_result.aaaa_count > 0
        ),

        "has_mx_record": int(
            dns_result.mx_count > 0
        ),

        "has_ns_record": int(
            dns_result.ns_count > 0
        ),

        "dns_error": (
            dns_result.dns_error
        ),
    }

    if include_rdap:
        rdap_result = (
            collect_rdap_information(
                domain
            )
        )

        features.update(
            {
                "rdap_available": int(
                    rdap_result.rdap_available
                ),

                "registration_date": (
                    rdap_result.registration_date
                ),

                "expiration_date": (
                    rdap_result.expiration_date
                ),

                "last_changed_date": (
                    rdap_result.last_changed_date
                ),

                "domain_age_days": (
                    rdap_result.domain_age_days
                ),

                "rdap_error": (
                    rdap_result.rdap_error
                ),
            }
        )

    else:
        features.update(
            {
                "rdap_available": 0,
                "registration_date": None,
                "expiration_date": None,
                "last_changed_date": None,
                "domain_age_days": None,
                "rdap_error": (
                    "RDAP collection disabled"
                ),
            }
        )

    return features