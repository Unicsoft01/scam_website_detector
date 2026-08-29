from dataclasses import dataclass, asdict
from typing import Optional

import dns.exception
import dns.resolver


@dataclass
class DNSResult:
    domain: str
    dns_resolved: bool

    a_records: list[str]
    aaaa_records: list[str]
    mx_records: list[str]
    ns_records: list[str]

    a_count: int
    aaaa_count: int
    mx_count: int
    ns_count: int

    dns_error: Optional[str] = None


def _resolve_record(
    domain: str,
    record_type: str,
) -> tuple[list[str], Optional[str]]:
    """
    Resolve a specific DNS record type.

    Returns:
        records, error_message
    """

    try:
        answers = dns.resolver.resolve(
            domain,
            record_type,
            lifetime=5.0,
        )

        records = []

        for answer in answers:
            value = str(answer).strip()

            if value:
                records.append(value)

        return records, None

    except dns.resolver.NXDOMAIN:
        return [], "NXDOMAIN"

    except dns.resolver.NoAnswer:
        return [], "NO_ANSWER"

    except dns.resolver.NoNameservers:
        return [], "NO_NAMESERVERS"

    except dns.exception.Timeout:
        return [], "TIMEOUT"

    except Exception as error:
        return [], str(error)


def collect_dns_information(
    domain: str
) -> DNSResult:
    """
    Collect selected DNS records.

    Missing records are represented as empty lists.
    The function should not crash when DNS information is unavailable.
    """

    a_records, a_error = _resolve_record(
        domain,
        "A",
    )

    aaaa_records, aaaa_error = _resolve_record(
        domain,
        "AAAA",
    )

    mx_records, mx_error = _resolve_record(
        domain,
        "MX",
    )

    ns_records, ns_error = _resolve_record(
        domain,
        "NS",
    )

    dns_resolved = bool(
        a_records
        or aaaa_records
        or mx_records
        or ns_records
    )

    errors = [
        error
        for error in [
            a_error,
            aaaa_error,
            mx_error,
            ns_error,
        ]
        if error is not None
    ]

    dns_error = (
        "; ".join(errors)
        if not dns_resolved and errors
        else None
    )

    return DNSResult(
        domain=domain,
        dns_resolved=dns_resolved,

        a_records=a_records,
        aaaa_records=aaaa_records,
        mx_records=mx_records,
        ns_records=ns_records,

        a_count=len(a_records),
        aaaa_count=len(aaaa_records),
        mx_count=len(mx_records),
        ns_count=len(ns_records),

        dns_error=dns_error,
    )


def dns_result_to_dict(
    result: DNSResult
) -> dict:
    return asdict(result)