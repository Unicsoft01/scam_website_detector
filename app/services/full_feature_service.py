from dataclasses import (
    asdict,
    dataclass,
)
from time import perf_counter
from typing import Any, Optional

from app.services.behavioural_observation_service import (
    build_behavioural_observation,
)

from app.services.heuristic_observation_service import (
    build_heuristic_observation,
)


@dataclass
class FullFeatureResult:
    url: str

    heuristic_success: bool
    heuristic_complete: bool

    behavioural_success: bool
    hybrid_success: bool

    heuristic_features: dict
    behavioural_features: dict

    heuristic_metadata: dict
    behavioural_metadata: dict

    heuristic_error: Optional[str]
    behavioural_error: Optional[str]

    heuristic_duration_ms: float
    behavioural_duration_ms: float
    total_duration_ms: float


def _validate_feature_dictionary(
    features: dict,
    feature_group: str,
) -> None:
    """
    Ensure candidate model features contain only
    numerical values, booleans, or explicit missing values.

    Strings or arbitrary objects are rejected because
    metadata must not silently enter the ML feature vector.
    """

    for name, value in features.items():

        if value is None:
            continue

        if isinstance(
            value,
            (
                bool,
                int,
                float,
            ),
        ):
            continue

        raise ValueError(
            (
                f"{feature_group} feature "
                f"'{name}' contains a non-numeric "
                f"value of type "
                f"{type(value).__name__}: "
                f"{value!r}"
            )
        )


def extract_full_features(
    url: str,
    include_rdap: bool = True,
    observation_time_ms: int = 2000,
) -> FullFeatureResult:
    """
    Run heuristic and behavioural extraction for one URL.

    Ground-truth labels are not used here.
    No classification is performed.
    """

    total_start = perf_counter()

    heuristic_features: dict[str, Any] = {}
    behavioural_features: dict[str, Any] = {}

    heuristic_metadata: dict[str, Any] = {}
    behavioural_metadata: dict[str, Any] = {}

    heuristic_error = None
    behavioural_error = None

    # =====================================================
    # HEURISTIC EXTRACTION
    # =====================================================

    heuristic_start = perf_counter()

    try:
        heuristic_result = (
            build_heuristic_observation(
                url,
                include_rdap=include_rdap,
            )
        )

        heuristic_success = bool(
            heuristic_result.get(
                "success"
            )
        )

        heuristic_features = (
            heuristic_result.get(
                "features"
            )
            or {}
        )

        heuristic_metadata = (
            heuristic_result.get(
                "metadata"
            )
            or {}
        )

        if heuristic_success:
            _validate_feature_dictionary(
                heuristic_features,
                "heuristic",
            )

        if not heuristic_success:
            heuristic_error = str(
                heuristic_metadata.get(
                    "error"
                )
                or heuristic_metadata.get(
                    "error_message"
                )
                or "Heuristic extraction failed."
            )

    except Exception as error:
        heuristic_success = False

        heuristic_features = {}
        heuristic_metadata = {}

        heuristic_error = (
            f"{error.__class__.__name__}: "
            f"{error}"
        )

    heuristic_duration_ms = (
        perf_counter()
        - heuristic_start
    ) * 1000

    # A successful function call is not necessarily
    # a complete X_H. Phase 10 requires usable HTML
    # for the complete HTML/static component.
    heuristic_complete = bool(
        heuristic_success
        and heuristic_metadata.get(
            "html_available"
        )
        is True
    )

    # =====================================================
    # BEHAVIOURAL EXTRACTION
    # =====================================================

    behavioural_start = perf_counter()

    try:
        behavioural_result = (
            build_behavioural_observation(
                url,
                observation_time_ms=(
                    observation_time_ms
                ),
            )
        )

        behavioural_success = bool(
            behavioural_result.get(
                "success"
            )
        )

        behavioural_features = (
            behavioural_result.get(
                "features"
            )
            or {}
        )

        behavioural_metadata = (
            behavioural_result.get(
                "metadata"
            )
            or {}
        )

        if behavioural_success:
            _validate_feature_dictionary(
                behavioural_features,
                "behavioural",
            )

        if not behavioural_success:
            behavioural_error = str(
                behavioural_metadata.get(
                    "error_message"
                )
                or behavioural_metadata.get(
                    "error_type"
                )
                or "Behavioural extraction failed."
            )

    except Exception as error:
        behavioural_success = False

        behavioural_features = {}
        behavioural_metadata = {}

        behavioural_error = (
            f"{error.__class__.__name__}: "
            f"{error}"
        )

    behavioural_duration_ms = (
        perf_counter()
        - behavioural_start
    ) * 1000

    # =====================================================
    # HYBRID COMPLETENESS
    # =====================================================

    hybrid_success = bool(
        heuristic_complete
        and behavioural_success
    )

    total_duration_ms = (
        perf_counter()
        - total_start
    ) * 1000

    return FullFeatureResult(
        url=url,

        heuristic_success=(
            heuristic_success
        ),

        heuristic_complete=(
            heuristic_complete
        ),

        behavioural_success=(
            behavioural_success
        ),

        hybrid_success=(
            hybrid_success
        ),

        heuristic_features=(
            heuristic_features
        ),

        behavioural_features=(
            behavioural_features
        ),

        heuristic_metadata=(
            heuristic_metadata
        ),

        behavioural_metadata=(
            behavioural_metadata
        ),

        heuristic_error=(
            heuristic_error
        ),

        behavioural_error=(
            behavioural_error
        ),

        heuristic_duration_ms=round(
            heuristic_duration_ms,
            3,
        ),

        behavioural_duration_ms=round(
            behavioural_duration_ms,
            3,
        ),

        total_duration_ms=round(
            total_duration_ms,
            3,
        ),
    )


def full_feature_result_to_dict(
    result: FullFeatureResult,
) -> dict:
    return asdict(
        result
    )