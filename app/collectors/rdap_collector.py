from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

import httpx


@dataclass
class RDAPResult:
    domain: str
    rdap_available: bool

    registration_date: Optional[str]
    expiration_date: Optional[str]
    last_changed_date: Optional[str]

    domain_age_days: Optional[int]

    rdap_error: Optional[str] = None


def _parse_rdap_datetime(
    value: Optional[str]
) -> Optional[datetime]:
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=timezone.utc
            )

        return parsed

    except Exception:
        return None


def _extract_event_date(
    events: list,
    action_names: set[str],
) -> Optional[str]:
    for event in events:
        action = (
            str(
                event.get(
                    "eventAction",
                    ""
                )
            )
            .strip()
            .lower()
        )

        if action in action_names:
            value = event.get(
                "eventDate"
            )

            if value:
                return str(value)

    return None


def collect_rdap_information(
    domain: str
) -> RDAPResult:
    """
    Query public RDAP registration data where available.

    Missing or unavailable RDAP information is represented explicitly
    rather than treated as evidence of scam or legitimacy.
    """

    url = (
        "https://rdap.org/domain/"
        f"{domain}"
    )

    try:
        with httpx.Client(
            timeout=10.0,
            follow_redirects=False,
            headers={
                "User-Agent": (
                    "Scam-Website-Detection-Research/1.0"
                )
            },
        ) as client:
            response = client.get(
                url
            )

        if response.status_code != 200:
            return RDAPResult(
                domain=domain,
                rdap_available=False,
                registration_date=None,
                expiration_date=None,
                last_changed_date=None,
                domain_age_days=None,
                rdap_error=(
                    f"HTTP {response.status_code}"
                ),
            )

        data = response.json()

        events = data.get(
            "events",
            []
        )

        registration_date = (
            _extract_event_date(
                events,
                {
                    "registration"
                },
            )
        )

        expiration_date = (
            _extract_event_date(
                events,
                {
                    "expiration"
                },
            )
        )

        last_changed_date = (
            _extract_event_date(
                events,
                {
                    "last changed",
                    "last update",
                    "last updated",
                },
            )
        )

        registration_dt = (
            _parse_rdap_datetime(
                registration_date
            )
        )

        domain_age_days = None

        if registration_dt:
            now = datetime.now(
                timezone.utc
            )

            domain_age_days = (
                now
                - registration_dt
            ).days

            if domain_age_days < 0:
                domain_age_days = None

        return RDAPResult(
            domain=domain,
            rdap_available=True,
            registration_date=registration_date,
            expiration_date=expiration_date,
            last_changed_date=last_changed_date,
            domain_age_days=domain_age_days,
            rdap_error=None,
        )

    except httpx.TimeoutException:
        return RDAPResult(
            domain=domain,
            rdap_available=False,
            registration_date=None,
            expiration_date=None,
            last_changed_date=None,
            domain_age_days=None,
            rdap_error="TIMEOUT",
        )

    except Exception as error:
        return RDAPResult(
            domain=domain,
            rdap_available=False,
            registration_date=None,
            expiration_date=None,
            last_changed_date=None,
            domain_age_days=None,
            rdap_error=str(error),
        )


def rdap_result_to_dict(
    result: RDAPResult
) -> dict:
    return asdict(result)