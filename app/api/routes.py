from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    get_scan_service,
)

from app.api.schemas import (
    HealthResponse,
    ModelResultResponse,
    ScanHistoryItem,
    ScanHistoryResponse,
    ScanRequest,
    ScanResultResponse,
    ScanSubmissionResponse,
)

from app.services.prediction_service import (
    prediction_class_name,
)

from app.services.scan_query_service import (
    ScanQueryService,
)


router = APIRouter()


@router.get(
    "/",
    tags=["Application"],
)
def home():

    return {
        "application": (
            "Real-Time Scam Website "
            "Detection System"
        ),
        "status": "running",
        "documentation": "/docs",
        "api": "/api",
    }


@router.get(
    "/api",
    tags=["Application"],
)
def api_information():

    return {
        "name": (
            "Scam Website Detection API"
        ),
        "version": "1.0.0",
        "classification": [
            "Legitimate Website",
            "Scam Website",
        ],
        "endpoints": {
            "submit_scan": (
                "POST /api/scans"
            ),
            "scan_result": (
                "GET /api/scans/{scan_id}"
            ),
            "scan_history": (
                "GET /api/scans"
            ),
            "health": (
                "GET /health"
            ),
        },
    }


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health_check(
    db: Session = Depends(
        get_db
    ),
):

    try:

        db.execute(
            text("SELECT 1")
        )

        database_status = (
            "connected"
        )

    except Exception:

        database_status = (
            "unavailable"
        )

        raise HTTPException(
            status_code=(
                status
                .HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "Database health check failed."
            ),
        )

    return HealthResponse(
        status="healthy",
        application="running",
        database=database_status,
    )


@router.post(
    "/api/scans",
    response_model=(
        ScanSubmissionResponse
    ),
    status_code=(
        status.HTTP_200_OK
    ),
    tags=["Scans"],
)
def submit_scan(
    request: ScanRequest,

    scan_service=Depends(
        get_scan_service
    ),
):

    # Request body validation has already
    # succeeded before execution reaches
    # this point.

    if scan_service is None:

        raise HTTPException(
            status_code=(
                status
                .HTTP_503_SERVICE_UNAVAILABLE
            ),
            detail=(
                "The scan runtime has not yet "
                "been connected to the approved "
                "validator, collectors and "
                "runtime model package."
            ),
        )

    try:

        response = (
            scan_service.scan(
                request.url
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(
                error
            ),
        ) from error

    return ScanSubmissionResponse(
        scan_id=response.scan_id,

        submitted_url=(
            response.submitted_url
        ),

        normalized_url=(
            response.normalized_url
        ),

        status=response.status,

        behavioural_available=(
            response
            .behavioural_available
        ),

        primary_configuration=(
            response
            .primary_configuration
        ),

        predicted_label=(
            response.predicted_label
        ),

        predicted_class=(
            response.predicted_class
        ),

        scam_probability=(
            response.scam_probability
        ),

        message=response.message,
    )


@router.get(
    "/api/scans/{scan_id}",
    response_model=ScanResultResponse,
    tags=["Scans"],
)
def retrieve_scan(
    scan_id: int,

    db: Session = Depends(
        get_db
    ),
):

    if scan_id <= 0:

        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "scan_id must be "
                "greater than zero."
            ),
        )

    service = ScanQueryService(
        db
    )

    scan = service.get_scan(
        scan_id
    )

    if scan is None:

        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Scan not found.",
        )

    results = service.get_results(
        scan_id
    )

    result_responses = []

    for result in results:

        if (
            result.predicted_label
            is None
        ):

            continue

        result_responses.append(
            ModelResultResponse(
                configuration=(
                    result.configuration
                ),

                scam_probability=(
                    result
                    .scam_probability
                ),

                threshold_used=(
                    result
                    .threshold_used
                ),

                predicted_label=(
                    result
                    .predicted_label
                ),

                predicted_class=(
                    prediction_class_name(
                        result
                        .predicted_label
                    )
                ),

                model_version=(
                    result.model_version
                ),

                response_time_ms=(
                    result
                    .response_time_ms
                ),
            )
        )

    return ScanResultResponse(
        scan_id=scan.scan_id,

        submitted_url=(
            scan.submitted_url
        ),

        normalized_url=(
            scan.normalized_url
        ),

        registrable_domain=(
            scan.registrable_domain
        ),

        scan_status=(
            scan.scan_status
        ),

        behavioural_available=(
            scan.behavioural_available
        ),

        initiated_at=(
            scan.initiated_at
        ),

        completed_at=(
            scan.completed_at
        ),

        error_code=(
            scan.error_code
        ),

        error_message=(
            scan.error_message
        ),

        results=(
            result_responses
        ),
    )


@router.get(
    "/api/scans",
    response_model=ScanHistoryResponse,
    tags=["Scans"],
)
def scan_history(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),

    offset: int = Query(
        default=0,
        ge=0,
    ),

    db: Session = Depends(
        get_db
    ),
):

    service = ScanQueryService(
        db
    )

    total, scans = (
        service.get_history(
            limit=limit,
            offset=offset,
        )
    )

    items = [
        ScanHistoryItem(
            scan_id=scan.scan_id,

            submitted_url=(
                scan.submitted_url
            ),

            normalized_url=(
                scan.normalized_url
            ),

            registrable_domain=(
                scan
                .registrable_domain
            ),

            scan_status=(
                scan.scan_status
            ),

            behavioural_available=(
                scan
                .behavioural_available
            ),

            initiated_at=(
                scan.initiated_at
            ),

            completed_at=(
                scan.completed_at
            ),
        )
        for scan in scans
    ]

    return ScanHistoryResponse(
        total=total,
        limit=limit,
        offset=offset,
        scans=items,
    )