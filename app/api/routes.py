from fastapi import APIRouter

from app.api.schemas import URLScanRequest
from app.core.url_security import (
    get_registrable_domain,
    is_public_destination,
    validate_url,
)

# Extract URL-level heuristic features
from app.features.url_features import (
    extract_url_features,
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

@router.post(
    "/url-features"
)
def get_url_features(
    request: URLScanRequest
):
    validation = validate_url(
        request.url
    )

    if not validation.is_valid:
        return {
            "success": False,
            "reason": validation.reason,
            "features": None,
        }

    features = (
        extract_url_features(
            validation.normalized_url
        )
    )

    return {
        "success": True,
        "normalized_url": (
            validation.normalized_url
        ),
        "features": features,
    }