from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    Request,
)

from fastapi.responses import (
    HTMLResponse,
)

from fastapi.templating import (
    Jinja2Templates,
)

from sqlalchemy.orm import Session

from app.api.dependencies import get_db

from app.services.scan_query_service import (
    ScanQueryService,
)

from app.services.explanation_service import (
    ExplanationService,
)

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


def _probability_percent(
    value: float | None,
) -> str | None:

    if value is None:
        return None

    return f"{float(value) * 100:.2f}"


def _find_result(
    results: list[Any],
    configuration: str,
):

    for result in results:

        if result.configuration == configuration:
            return result

    return None


def _humanize_feature_name(
    name: str,
) -> str:

    if name.startswith("h_"):
        name = name[2:]

    elif name.startswith("b_"):
        name = name[2:]

    return (
        name
        .replace("_", " ")
        .strip()
        .title()
    )


def _extract_detected_indicators(
    feature_data: dict | None,
    prefix: str,
    limit: int = 6,
) -> list[dict]:

    if not isinstance(
        feature_data,
        dict,
    ):
        return []

    indicators = []

    for name, value in feature_data.items():

        if not str(name).startswith(
            prefix
        ):
            continue

        # Display only observations carrying
        # a non-zero/positive signal.
        #
        # This is descriptive evidence only;
        # it is not a causal explanation of
        # the Random Forest prediction.

        try:
            numeric_value = float(value)

        except (
            TypeError,
            ValueError,
        ):
            continue

        if numeric_value <= 0:
            continue

        indicators.append(
            {
                "name":
                    _humanize_feature_name(
                        str(name)
                    ),

                "value": value,
            }
        )

    return indicators[:limit]


@router.get(
    "/",
    response_class=HTMLResponse,
    tags=["Web Interface"],
)
def home_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "page_title":
                "Scam Website Detector",
        },
    )


@router.get(
    "/results/{scan_id}",
    response_class=HTMLResponse,
    tags=["Web Interface"],
)
def result_page(
    request: Request,
    scan_id: int,
    db: Session = Depends(get_db),
):

    service = ScanQueryService(
        db
    )

    scan = service.get_scan(
        scan_id
    )

    if scan is None:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            status_code=404,
            context={
                "page_title":
                    "Scan Not Found",

                "error_title":
                    "Scan Not Found",

                "error_message":
                    (
                        "The requested scan "
                        "record does not exist."
                    ),
            },
        )

    results = service.get_results(
        scan_id
    )

    heuristic = _find_result(
        results,
        "heuristic",
    )

    behavioural = _find_result(
        results,
        "behavioural",
    )

    hybrid = _find_result(
        results,
        "hybrid",
    )

    heuristic_observation = (
        service
        .get_heuristic_observation(
            scan_id
        )
    )

    behavioural_observation = (
        service
        .get_behavioural_observation(
            scan_id
        )
    )

    explanation_service = (
        ExplanationService()
    )


    heuristic_feature_data = (
        heuristic_observation.feature_data
        if heuristic_observation
        else None
    )


    behavioural_feature_data = (
        behavioural_observation.feature_data
        if behavioural_observation
        else None
    )


    evidence_indicators = (
        explanation_service.explain(
            heuristic_features=(
                heuristic_feature_data
            ),
            behavioural_features=(
                behavioural_feature_data
            ),
            max_indicators=10,
        )
    )

    heuristic_indicators = (
        _extract_detected_indicators(
            (
                heuristic_observation
                .feature_data
                if heuristic_observation
                else None
            ),
            prefix="h_",
        )
    )

    behavioural_indicators = (
        _extract_detected_indicators(
            (
                behavioural_observation
                .feature_data
                if behavioural_observation
                else None
            ),
            prefix="b_",
        )
    )

    primary = (
        hybrid
        or heuristic
        or behavioural
    )

    if (
        primary is not None
        and primary.predicted_label
        is not None
    ):

        predicted_class = (
            "Scam Website"
            if primary.predicted_label == 1
            else "Legitimate Website"
        )

    else:

        predicted_class = None

    total_duration_ms = None

    if (
        scan.initiated_at
        and scan.completed_at
    ):

        total_duration_ms = (
            scan.completed_at
            - scan.initiated_at
        ).total_seconds() * 1000.0

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "page_title":
                f"Scan #{scan.scan_id}",

            "scan": scan,

            "heuristic":
                heuristic,

            "behavioural":
                behavioural,

            "hybrid":
                hybrid,

            "primary":
                primary,

            "predicted_class":
                predicted_class,

            "heuristic_probability":
                _probability_percent(
                    heuristic
                    .scam_probability
                    if heuristic
                    else None
                ),

            "behavioural_probability":
                _probability_percent(
                    behavioural
                    .scam_probability
                    if behavioural
                    else None
                ),

            "hybrid_probability":
                _probability_percent(
                    hybrid
                    .scam_probability
                    if hybrid
                    else None
                ),

            "heuristic_indicators":
                heuristic_indicators,

            "behavioural_indicators":
                behavioural_indicators,

            "total_duration_ms":
                total_duration_ms,

            "evidence_indicators":
                evidence_indicators,
        },
    )


@router.get(
    "/history",
    response_class=HTMLResponse,
    tags=["Web Interface"],
)
def history_page(
    request: Request,
    db: Session = Depends(get_db),
):

    service = ScanQueryService(
        db
    )

    total, scans = (
        service.get_history(
            limit=100,
            offset=0,
        )
    )

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "page_title":
                "Scan History",

            "total": total,
            "scans": scans,
        },
    )