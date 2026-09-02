from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from time import perf_counter
from typing import Any, Optional, Protocol

from app.schemas.scan import (
    ModelDecision,
    ScanResponse,
)

from app.services.prediction_service import (
    PredictionOutput,
    PredictionService,
    prediction_class_name,
)

from app.services.scan_repository import (
    ScanRepository,
)


# =====================================================
# Dependency contracts
# =====================================================


@dataclass
class ValidationResult:
    valid: bool
    normalized_url: Optional[str]
    registrable_domain: Optional[str]
    reason: Optional[str] = None


@dataclass
class EvidenceResult:
    success: bool
    features: Optional[dict]
    extraction_time_ms: Optional[float]
    failure_reason: Optional[str] = None

    observation_window_ms: Optional[
        float
    ] = None

    events: Optional[list[dict]] = None


class URLValidator(Protocol):

    def validate(
        self,
        url: str,
    ) -> ValidationResult:
        ...


class HeuristicCollector(Protocol):

    def collect(
        self,
        url: str,
    ) -> EvidenceResult:
        ...


class BehaviouralCollector(Protocol):

    def collect(
        self,
        url: str,
    ) -> EvidenceResult:
        ...


# =====================================================
# Main coordinator
# =====================================================


class ScanService:

    def __init__(
        self,
        repository: ScanRepository,
        validator: URLValidator,
        heuristic_collector: (
            HeuristicCollector
        ),
        behavioural_collector: (
            BehaviouralCollector
        ),
        prediction_service: (
            PredictionService
        ),
    ):

        self.repository = repository
        self.validator = validator

        self.heuristic_collector = (
            heuristic_collector
        )

        self.behavioural_collector = (
            behavioural_collector
        )

        self.prediction_service = (
            prediction_service
        )

    def scan(
        self,
        submitted_url: str,
    ) -> ScanResponse:

        # ---------------------------------------------
        # 1. Basic submission check.
        # ---------------------------------------------

        if not isinstance(
            submitted_url,
            str,
        ):

            raise TypeError(
                "submitted_url must be a string."
            )

        submitted_url = (
            submitted_url.strip()
        )

        if not submitted_url:

            raise ValueError(
                "A URL is required."
            )

        # We need a placeholder normalized URL because
        # the database currently defines the field as
        # non-nullable. It will be replaced immediately
        # after successful validation.
        initial_hash = sha256(
            submitted_url.encode(
                "utf-8"
            )
        ).hexdigest()

        scan = self.repository.create_scan(
            submitted_url=submitted_url,
            normalized_url=submitted_url,
            url_hash=initial_hash,
            registrable_domain=None,
        )

        scan_id = scan.scan_id

        # Preserve the scan record before any external
        # validation, network collection, browser
        # execution or model inference begins.
        self.repository.commit()

        try:

            self.repository.add_event(
                scan_id=scan_id,
                event_type="scan_started",
                event_name=(
                    "scan_processing_started"
                ),
            )

            # -----------------------------------------
            # 2. Validate and normalize.
            # -----------------------------------------

            validation = (
                self._validate_url(
                    submitted_url
                )
            )

            if not validation.valid:

                return (
                    self._finish_validation_failure(
                        scan=scan,
                        submitted_url=(
                            submitted_url
                        ),
                        reason=(
                            validation.reason
                            or "URL validation failed."
                        ),
                    )
                )

            normalized_url = (
                validation.normalized_url
            )

            if normalized_url is None:

                raise RuntimeError(
                    (
                        "Validator reported success "
                        "without a normalized URL."
                    )
                )

            normalized_hash = sha256(
                normalized_url.encode(
                    "utf-8"
                )
            ).hexdigest()

            self.repository.update_normalized_scan(
                scan=scan,
                normalized_url=normalized_url,
                url_hash=normalized_hash,
                registrable_domain=(
                    validation
                    .registrable_domain
                ),
            )

            self.repository.add_event(
                scan_id=scan_id,
                event_type="validation",
                event_name="url_validated",
                event_data={
                    "registrable_domain":
                        validation
                        .registrable_domain
                },
            )

            # -----------------------------------------
            # 3. Collect heuristic evidence.
            # -----------------------------------------

            heuristic_evidence = (
                self._collect_heuristic(
                    scan_id=scan_id,
                    normalized_url=(
                        normalized_url
                    ),
                )
            )

            # -----------------------------------------
            # 4. Collect behavioural evidence.
            # -----------------------------------------

            behavioural_evidence = (
                self._collect_behavioural(
                    scan_id=scan_id,
                    normalized_url=(
                        normalized_url
                    ),
                )
            )

            self.repository.set_behavioural_available(
                scan=scan,
                available=(
                    behavioural_evidence
                    .success
                ),
            )

            # -----------------------------------------
            # 5. Run available models.
            # -----------------------------------------

            heuristic_prediction = None
            behavioural_prediction = None
            hybrid_prediction = None

            if heuristic_evidence.success:

                heuristic_prediction = (
                    self._run_heuristic_model(
                        scan_id=scan_id,
                        feature_data=(
                            heuristic_evidence
                            .features
                            or {}
                        ),
                    )
                )

            if behavioural_evidence.success:

                behavioural_prediction = (
                    self._run_behavioural_model(
                        scan_id=scan_id,
                        feature_data=(
                            behavioural_evidence
                            .features
                            or {}
                        ),
                    )
                )

            # -----------------------------------------
            # 6. Fuse only if both probabilities exist.
            # -----------------------------------------

            if (
                heuristic_prediction
                is not None
                and behavioural_prediction
                is not None
            ):

                hybrid_prediction = (
                    self._run_hybrid_model(
                        scan_id=scan_id,
                        heuristic_prediction=(
                            heuristic_prediction
                        ),
                        behavioural_prediction=(
                            behavioural_prediction
                        ),
                    )
                )

            # -----------------------------------------
            # 7. Determine primary user decision.
            # -----------------------------------------

            response = (
                self._build_final_response(
                    scan=scan,
                    submitted_url=submitted_url,
                    normalized_url=(
                        normalized_url
                    ),
                    heuristic_prediction=(
                        heuristic_prediction
                    ),
                    behavioural_prediction=(
                        behavioural_prediction
                    ),
                    hybrid_prediction=(
                        hybrid_prediction
                    ),
                )
            )

            self.repository.commit()

            return response

        except Exception as error:

            self.repository.rollback()

            try:

                self.repository.fail_scan(
                    scan=scan,
                    error_code=(
                        "internal_application_error"
                    ),
                    error_message=(
                        "An internal application error "
                        "prevented the scan from being "
                        "completed."
                    ),
                )

                self.repository.add_log(
                    level="ERROR",
                    component="ScanService",
                    message=(
                        "Unexpected scan failure."
                    ),
                    scan_id=scan_id,
                    details={
                        "exception_type":
                            type(error).__name__,
                        "exception_message":
                            str(error),
                    },
                )

                self.repository.commit()

            except Exception:

                self.repository.rollback()

            return ScanResponse(
                scan_id=scan_id,
                submitted_url=submitted_url,
                normalized_url=None,
                status="failed",
                behavioural_available=False,
                primary_configuration=None,
                predicted_label=None,
                predicted_class=None,
                scam_probability=None,
                heuristic_result=None,
                behavioural_result=None,
                hybrid_result=None,
                message=(
                    "An internal application error "
                    "prevented the scan from being "
                    "completed."
                ),
                error_code=(
                    "internal_application_error"
                ),
                error_message=(
                    "An internal application error "
                    "prevented the scan from being "
                    "completed."
                ),
            )
    # =================================================
    # Validation
    # =================================================

    def _validate_url(
        self,
        url: str,
    ) -> ValidationResult:

        return self.validator.validate(
            url
        )

    def _finish_validation_failure(
        self,
        scan,
        submitted_url: str,
        reason: str,
    ) -> ScanResponse:

        self.repository.add_event(
            scan_id=scan.scan_id,
            event_type="validation",
            event_name="url_rejected",
            event_data={
                "reason": reason
            },
        )

        self.repository.fail_scan(
            scan=scan,
            error_code="URL_VALIDATION_FAILED",
            error_message=reason,
        )

        self.repository.commit()

        return ScanResponse(
            scan_id=scan.scan_id,
            submitted_url=submitted_url,
            normalized_url=None,
            status="failed",
            behavioural_available=None,
            primary_configuration=None,
            predicted_label=None,
            predicted_class=None,
            scam_probability=None,
            heuristic_result=None,
            behavioural_result=None,
            hybrid_result=None,
            message=reason,
        )

    # =================================================
    # Evidence collection
    # =================================================

    def _collect_heuristic(
        self,
        scan_id: int,
        normalized_url: str,
    ) -> EvidenceResult:

        start = perf_counter()

        try:

            result = (
                self.heuristic_collector
                .collect(
                    normalized_url
                )
            )

        except Exception as error:

            elapsed = (
                perf_counter()
                - start
            ) * 1000.0

            result = EvidenceResult(
                success=False,
                features=None,
                extraction_time_ms=elapsed,
                failure_reason=str(
                    error
                ),
            )

        self.repository.save_heuristic_observation(
            scan_id=scan_id,
            feature_data=result.features,
            extraction_status=(
                "complete"
                if result.success
                else "failed"
            ),
            extraction_time_ms=(
                result.extraction_time_ms
            ),
            failure_reason=(
                result.failure_reason
            ),
        )

        self.repository.add_event(
            scan_id=scan_id,
            event_type="heuristic_collection",
            event_name=(
                "heuristic_complete"
                if result.success
                else "heuristic_failed"
            ),
            event_data={
                "success":
                    result.success,

                "failure_reason":
                    result.failure_reason,
            },
        )

        return result

    def _collect_behavioural(
        self,
        scan_id: int,
        normalized_url: str,
    ) -> EvidenceResult:

        start = perf_counter()

        try:

            result = (
                self.behavioural_collector
                .collect(
                    normalized_url
                )
            )

        except Exception as error:

            elapsed = (
                perf_counter()
                - start
            ) * 1000.0

            result = EvidenceResult(
                success=False,
                features=None,
                extraction_time_ms=elapsed,
                failure_reason=str(
                    error
                ),
            )

        self.repository.save_behavioural_observation(
            scan_id=scan_id,
            feature_data=result.features,
            extraction_status=(
                "complete"
                if result.success
                else "failed"
            ),
            observation_window_ms=(
                result
                .observation_window_ms
            ),
            extraction_time_ms=(
                result.extraction_time_ms
            ),
            failure_reason=(
                result.failure_reason
            ),
        )

        if result.events:

            for event in result.events:

                self.repository.add_event(
                    scan_id=scan_id,

                    event_type=str(
                        event.get(
                            "event_type",
                            "behavioural_event",
                        )
                    ),

                    event_name=(
                        event.get(
                            "event_name"
                        )
                    ),

                    event_data=(
                        event.get(
                            "event_data"
                        )
                    ),
                )

        self.repository.add_event(
            scan_id=scan_id,
            event_type=(
                "behavioural_collection"
            ),
            event_name=(
                "behavioural_complete"
                if result.success
                else "behavioural_failed"
            ),
            event_data={
                "success":
                    result.success,

                "failure_reason":
                    result.failure_reason,
            },
        )

        return result

    # =================================================
    # Model execution
    # =================================================

    def _run_heuristic_model(
        self,
        scan_id: int,
        feature_data: dict,
    ) -> PredictionOutput:

        prediction = (
            self.prediction_service
            .predict_heuristic(
                feature_data
            )
        )

        self._store_prediction(
            scan_id,
            prediction,
            evidence_status="complete",
        )

        return prediction

    def _run_behavioural_model(
        self,
        scan_id: int,
        feature_data: dict,
    ) -> PredictionOutput:

        prediction = (
            self.prediction_service
            .predict_behavioural(
                feature_data
            )
        )

        self._store_prediction(
            scan_id,
            prediction,
            evidence_status="complete",
        )

        return prediction

    def _run_hybrid_model(
        self,
        scan_id: int,
        heuristic_prediction: (
            PredictionOutput
        ),
        behavioural_prediction: (
            PredictionOutput
        ),
    ) -> PredictionOutput:

        prediction = (
            self.prediction_service.fuse(
                heuristic_probability=(
                    heuristic_prediction
                    .probability
                ),
                behavioural_probability=(
                    behavioural_prediction
                    .probability
                ),
            )
        )

        self._store_prediction(
            scan_id,
            prediction,
            evidence_status=(
                "complete_hybrid_evidence"
            ),
        )

        return prediction

    def _store_prediction(
        self,
        scan_id: int,
        prediction: PredictionOutput,
        evidence_status: str,
    ) -> None:

        self.repository.save_analysis_result(
            scan_id=scan_id,

            configuration=(
                prediction.configuration
            ),

            scam_probability=(
                prediction.probability
            ),

            threshold_used=(
                prediction.threshold
            ),

            predicted_label=(
                prediction.predicted_label
            ),

            model_version=(
                self.prediction_service
                .model_version
            ),

            response_time_ms=(
                prediction.response_time_ms
            ),

            evidence_status=(
                evidence_status
            ),
        )

    # =================================================
    # Response construction
    # =================================================

    def _to_model_decision(
        self,
        prediction: Optional[
            PredictionOutput
        ],
    ) -> Optional[ModelDecision]:

        if prediction is None:

            return None

        return ModelDecision(
            configuration=(
                prediction.configuration
            ),

            scam_probability=(
                prediction.probability
            ),

            threshold=(
                prediction.threshold
            ),

            predicted_label=(
                prediction.predicted_label
            ),

            predicted_class=(
                prediction_class_name(
                    prediction
                    .predicted_label
                )
            ),

            model_version=(
                self.prediction_service
                .model_version
            ),
        )

    def _build_final_response(
        self,
        scan,
        submitted_url: str,
        normalized_url: str,
        heuristic_prediction: Optional[
            PredictionOutput
        ],
        behavioural_prediction: Optional[
            PredictionOutput
        ],
        hybrid_prediction: Optional[
            PredictionOutput
        ],
    ) -> ScanResponse:

        # ---------------------------------------------
        # Preferred case: complete hybrid evidence.
        # ---------------------------------------------

        if hybrid_prediction is not None:

            self.repository.complete_scan(
                scan
            )

            primary = hybrid_prediction

            message = (
                "Scan completed using "
                "heuristic and behavioural "
                "evidence."
            )

            primary_configuration = (
                "hybrid"
            )

        # ---------------------------------------------
        # Explicit heuristic fallback.
        # ---------------------------------------------

        elif heuristic_prediction is not None:

            self.repository.partial_scan(
                scan=scan,
                error_code=(
                    "BEHAVIOURAL_EVIDENCE_UNAVAILABLE"
                ),
                error_message=(
                    "Behavioural evidence was "
                    "unavailable. The returned "
                    "classification is an "
                    "RF-H heuristic fallback, "
                    "not a hybrid result."
                ),
            )

            primary = heuristic_prediction

            message = (
                "Behavioural evidence was "
                "unavailable. Result produced "
                "using the approved heuristic "
                "model only."
            )

            primary_configuration = (
                "heuristic_fallback"
            )

        # ---------------------------------------------
        # RF-B alone is recorded but not promoted to
        # the production primary decision because we
        # have not approved a behavioural-only
        # production fallback policy.
        # ---------------------------------------------

        elif behavioural_prediction is not None:

            self.repository.partial_scan(
                scan=scan,
                error_code=(
                    "HEURISTIC_EVIDENCE_UNAVAILABLE"
                ),
                error_message=(
                    "Behavioural evidence was "
                    "available but heuristic "
                    "evidence was unavailable. "
                    "No primary production "
                    "classification was issued."
                ),
            )

            return ScanResponse(
                scan_id=scan.scan_id,

                submitted_url=(
                    submitted_url
                ),

                normalized_url=(
                    normalized_url
                ),

                status="partial",

                behavioural_available=True,

                primary_configuration=None,

                predicted_label=None,

                predicted_class=None,

                scam_probability=None,

                heuristic_result=None,

                behavioural_result=(
                    self._to_model_decision(
                        behavioural_prediction
                    )
                ),

                hybrid_result=None,

                message=(
                    "RF-B was recorded for "
                    "diagnostic evidence, but "
                    "the application did not "
                    "issue a primary decision "
                    "without heuristic evidence."
                ),
            )

        else:

            self.repository.fail_scan(
                scan=scan,

                error_code=(
                    "NO_USABLE_EVIDENCE"
                ),

                error_message=(
                    "Neither heuristic nor "
                    "behavioural evidence could "
                    "be classified."
                ),
            )

            return ScanResponse(
                scan_id=scan.scan_id,

                submitted_url=(
                    submitted_url
                ),

                normalized_url=(
                    normalized_url
                ),

                status="failed",

                behavioural_available=False,

                primary_configuration=None,

                predicted_label=None,

                predicted_class=None,

                scam_probability=None,

                heuristic_result=None,

                behavioural_result=None,

                hybrid_result=None,

                message=(
                    "No usable evidence was "
                    "available for classification."
                ),
            )

        return ScanResponse(
            scan_id=scan.scan_id,

            submitted_url=submitted_url,

            normalized_url=normalized_url,

            status=scan.scan_status,

            behavioural_available=(
                scan.behavioural_available
            ),

            primary_configuration=(
                primary_configuration
            ),

            predicted_label=(
                primary.predicted_label
            ),

            predicted_class=(
                prediction_class_name(
                    primary.predicted_label
                )
            ),

            scam_probability=(
                primary.probability
            ),

            heuristic_result=(
                self._to_model_decision(
                    heuristic_prediction
                )
            ),

            behavioural_result=(
                self._to_model_decision(
                    behavioural_prediction
                )
            ),

            hybrid_result=(
                self._to_model_decision(
                    hybrid_prediction
                )
            ),

            message=message,
        )