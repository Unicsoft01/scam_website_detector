from collections.abc import Generator
from time import perf_counter

from fastapi import (
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.url_security import (
    get_registrable_domain,
    is_public_destination,
    validate_url,
)

from app.database.session import (
    SessionLocal,
)

from app.services.behavioural_observation_service import (
    build_behavioural_observation,
)

from app.services.heuristic_observation_service import (
    build_heuristic_observation,
)

from app.services.prediction_service import (
    PredictionService,
)

from app.services.scan_repository import (
    ScanRepository,
)

from app.services.scan_service import (
    EvidenceResult,
    ScanService,
    ValidationResult,
)


# =====================================================
# Database dependency
# =====================================================


def get_db() -> Generator[
    Session,
    None,
    None,
]:

    database = SessionLocal()

    try:
        yield database

    finally:
        database.close()


# =====================================================
# URL validator adapter
# =====================================================


class RuntimeURLValidator:
    """
    Adapter between the Phase 29 URL-security
    functions and the ScanService validator
    interface.

    Validation occurs in two stages:

    1. URL syntax/normalisation.
    2. Public-destination safety checking.
    """

    def validate(
        self,
        url: str,
    ) -> ValidationResult:

        validation = validate_url(
            url
        )

        if not validation.is_valid:

            return ValidationResult(
                valid=False,
                normalized_url=None,
                registrable_domain=None,
                reason=(
                    validation.reason
                    or "URL validation failed."
                ),
            )

        normalized_url = (
            validation.normalized_url
        )

        if normalized_url is None:

            return ValidationResult(
                valid=False,
                normalized_url=None,
                registrable_domain=None,
                reason=(
                    "URL validation did not "
                    "produce a normalized URL."
                ),
            )

        # ---------------------------------------------
        # SSRF/public-destination safety gate.
        # ---------------------------------------------

        allowed, reason = (
            is_public_destination(
                normalized_url
            )
        )

        if not allowed:

            return ValidationResult(
                valid=False,
                normalized_url=None,
                registrable_domain=None,
                reason=(
                    reason
                    or (
                        "The requested destination "
                        "is not permitted."
                    )
                ),
            )

        try:

            registrable_domain = (
                get_registrable_domain(
                    normalized_url
                )
            )

        except Exception:

            registrable_domain = None

        return ValidationResult(
            valid=True,
            normalized_url=normalized_url,
            registrable_domain=(
                registrable_domain
            ),
            reason=None,
        )


# =====================================================
# Heuristic collector adapter
# =====================================================


class RuntimeHeuristicCollector:
    """
    Convert the dictionary returned by
    build_heuristic_observation() into the
    EvidenceResult expected by ScanService.
    """

    def collect(
        self,
        url: str,
    ) -> EvidenceResult:

        start = perf_counter()

        try:

            result = (
                build_heuristic_observation(
                    url
                )
            )

        except Exception as error:

            elapsed_ms = (
                perf_counter()
                - start
            ) * 1000.0

            return EvidenceResult(
                success=False,
                features=None,
                extraction_time_ms=(
                    elapsed_ms
                ),
                failure_reason=str(
                    error
                ),
            )

        elapsed_ms = (
            perf_counter()
            - start
        ) * 1000.0

        success = bool(
            result.get(
                "success",
                False,
            )
        )

        features = result.get(
            "features"
        )

        if isinstance(
            features,
            dict,
        ):

            features = {
                (
                    key
                    if key.startswith("h_")
                    else f"h_{key}"
                ): value
                for key, value
                in features.items()
            }

        metadata = (
            result.get(
                "metadata"
            )
            or {}
        )

        if (
            success
            and not isinstance(
                features,
                dict,
            )
        ):

            return EvidenceResult(
                success=False,
                features=None,
                extraction_time_ms=(
                    elapsed_ms
                ),
                failure_reason=(
                    "Heuristic collection "
                    "completed without a valid "
                    "feature dictionary."
                ),
            )

        if not success:

            failure_reason = (
                metadata.get(
                    "error"
                )
                or (
                    "Heuristic evidence "
                    "collection failed."
                )
            )

            return EvidenceResult(
                success=False,
                features=features,
                extraction_time_ms=(
                    elapsed_ms
                ),
                failure_reason=str(
                    failure_reason
                ),
            )

        return EvidenceResult(
            success=True,
            features=features,
            extraction_time_ms=(
                elapsed_ms
            ),
            failure_reason=None,
        )


# =====================================================
# Behavioural collector adapter
# =====================================================


class RuntimeBehaviouralCollector:
    """
    Convert the dictionary returned by
    build_behavioural_observation() into the
    EvidenceResult expected by ScanService.
    """

    def __init__(
        self,
        observation_time_ms: int = 2000,
    ):

        self.observation_time_ms = (
            observation_time_ms
        )

    def collect(
        self,
        url: str,
    ) -> EvidenceResult:

        start = perf_counter()

        try:

            result = (
                build_behavioural_observation(
                    url,
                    observation_time_ms=(
                        self.observation_time_ms
                    ),
                )
            )

        except Exception as error:

            elapsed_ms = (
                perf_counter()
                - start
            ) * 1000.0

            return EvidenceResult(
                success=False,
                features=None,
                extraction_time_ms=(
                    elapsed_ms
                ),
                failure_reason=str(
                    error
                ),
                observation_window_ms=(
                    self.observation_time_ms
                ),
            )

        elapsed_ms = (
            perf_counter()
            - start
        ) * 1000.0

        success = bool(
            result.get(
                "success",
                False,
            )
        )

        features = result.get(
            "features"
        )

        if isinstance(
            features,
            dict,
        ):

            features = {
                (
                    key
                    if key.startswith("b_")
                    else f"b_{key}"
                ): value
                for key, value
                in features.items()
            }

        metadata = (
            result.get(
                "metadata"
            )
            or {}
        )

        if (
            success
            and not isinstance(
                features,
                dict,
            )
        ):

            return EvidenceResult(
                success=False,
                features=None,
                extraction_time_ms=(
                    elapsed_ms
                ),
                failure_reason=(
                    "Behavioural collection "
                    "completed without a valid "
                    "feature dictionary."
                ),
                observation_window_ms=(
                    self.observation_time_ms
                ),
            )

        if not success:

            failure_reason = (
                metadata.get(
                    "error_message"
                )
                or metadata.get(
                    "error_type"
                )
                or (
                    "Behavioural evidence "
                    "collection failed."
                )
            )

            return EvidenceResult(
                success=False,
                features=None,
                extraction_time_ms=(
                    elapsed_ms
                ),
                failure_reason=str(
                    failure_reason
                ),
                observation_window_ms=(
                    self.observation_time_ms
                ),
            )

        return EvidenceResult(
            success=True,
            features=features,
            extraction_time_ms=(
                elapsed_ms
            ),
            failure_reason=None,
            observation_window_ms=(
                self.observation_time_ms
            ),
        )


# =====================================================
# Production ScanService dependency
# =====================================================


def get_scan_service(
    db: Session = Depends(
        get_db
    ),
) -> ScanService:
    """
    Construct the production scan coordinator.

    The prediction service loads the approved
    runtime RF-H, RF-B and hybrid configuration
    from models/runtime/v1.0.0.
    """

    try:

        repository = (
            ScanRepository(
                db
            )
        )

        validator = (
            RuntimeURLValidator()
        )

        heuristic_collector = (
            RuntimeHeuristicCollector()
        )

        behavioural_collector = (
            RuntimeBehaviouralCollector(
                observation_time_ms=2000
            )
        )

        prediction_service = (
            PredictionService(
                model_version="1.0.0"
            )
        )

        return ScanService(
            repository=repository,
            validator=validator,
            heuristic_collector=(
                heuristic_collector
            ),
            behavioural_collector=(
                behavioural_collector
            ),
            prediction_service=(
                prediction_service
            ),
        )

    except (
        FileNotFoundError,
        ValueError,
        KeyError,
    ) as error:

        # Do not expose model paths, checksums or
        # internal configuration details to users.
        raise HTTPException(
            status_code=(
                status
                .HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "The scan runtime is currently "
                "unavailable because its approved "
                "model package could not be loaded."
            ),
        ) from error