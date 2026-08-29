from fastapi import APIRouter

from app.api.schemas import URLScanRequest
from app.core.url_security import (
    get_registrable_domain,
    is_public_destination,
    validate_url,
)


router = APIRouter()


@router.post(
    "/validate-url"
)
def validate_submitted_url(
    request: URLScanRequest
):
    validation = validate_url(
        request.url
    )

    if not validation.is_valid:
        return {
            "valid": False,
            "safe_destination": False,
            "normalized_url": None,
            "registrable_domain": None,
            "reason": validation.reason,
        }

    allowed, reason = (
        is_public_destination(
            validation.normalized_url
        )
    )

    return {
        "valid": True,
        "safe_destination": allowed,
        "normalized_url": (
            validation.normalized_url
        ),
        "registrable_domain": (
            get_registrable_domain(
                validation.normalized_url
            )
        ),
        "reason": reason,
    }