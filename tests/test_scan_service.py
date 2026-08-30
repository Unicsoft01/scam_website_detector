from dataclasses import dataclass

from app.services.scan_service import (
    EvidenceResult,
    ScanService,
    ValidationResult,
)

from app.services.prediction_service import (
    PredictionOutput,
)


@dataclass
class FakeScan:
    scan_id: int = 1
    scan_status: str = "processing"
    behavioural_available: bool | None = None


class FakeRepository:

    def __init__(self):

        self.scan = FakeScan()

        self.results = []

        self.committed = False

    def create_scan(
        self,
        **kwargs,
    ):

        return self.scan

    def update_normalized_scan(
        self,
        **kwargs,
    ):

        pass

    def add_event(
        self,
        **kwargs,
    ):

        pass

    def save_heuristic_observation(
        self,
        **kwargs,
    ):

        pass

    def save_behavioural_observation(
        self,
        **kwargs,
    ):

        pass

    def set_behavioural_available(
        self,
        scan,
        available,
    ):

        scan.behavioural_available = (
            available
        )

    def save_analysis_result(
        self,
        **kwargs,
    ):

        self.results.append(
            kwargs
        )

    def complete_scan(
        self,
        scan,
    ):

        scan.scan_status = "completed"

    def partial_scan(
        self,
        scan,
        **kwargs,
    ):

        scan.scan_status = "partial"

    def fail_scan(
        self,
        scan,
        **kwargs,
    ):

        scan.scan_status = "failed"

    def commit(
        self,
    ):

        self.committed = True

    def rollback(
        self,
    ):

        pass


class ValidValidator:

    def validate(
        self,
        url,
    ):

        return ValidationResult(
            valid=True,
            normalized_url=(
                "https://example.com/"
            ),
            registrable_domain=(
                "example.com"
            ),
        )


class InvalidValidator:

    def validate(
        self,
        url,
    ):

        return ValidationResult(
            valid=False,
            normalized_url=None,
            registrable_domain=None,
            reason="URL rejected.",
        )


class SuccessfulHeuristicCollector:

    def collect(
        self,
        url,
    ):

        return EvidenceResult(
            success=True,

            features={
                "h_fake": 1
            },

            extraction_time_ms=1.0,
        )


class SuccessfulBehaviouralCollector:

    def collect(
        self,
        url,
    ):

        return EvidenceResult(
            success=True,

            features={
                "b_fake": 1
            },

            extraction_time_ms=2.0,

            observation_window_ms=(
                1000.0
            ),

            events=[],
        )


class FailedBehaviouralCollector:

    def collect(
        self,
        url,
    ):

        return EvidenceResult(
            success=False,
            features=None,
            extraction_time_ms=2.0,
            failure_reason=(
                "Browser timeout."
            ),
        )


class FakePredictionService:

    model_version = "test-version"

    def predict_heuristic(
        self,
        feature_data,
    ):

        return PredictionOutput(
            configuration="heuristic",
            probability=0.70,
            threshold=0.50,
            predicted_label=1,
            response_time_ms=1.0,
        )

    def predict_behavioural(
        self,
        feature_data,
    ):

        return PredictionOutput(
            configuration="behavioural",
            probability=0.90,
            threshold=0.50,
            predicted_label=1,
            response_time_ms=1.0,
        )

    def fuse(
        self,
        heuristic_probability,
        behavioural_probability,
    ):

        return PredictionOutput(
            configuration="hybrid",
            probability=0.80,
            threshold=0.50,
            predicted_label=1,
            response_time_ms=0.1,
        )


def test_complete_hybrid_scan():

    repository = FakeRepository()

    service = ScanService(
        repository=repository,
        validator=ValidValidator(),

        heuristic_collector=(
            SuccessfulHeuristicCollector()
        ),

        behavioural_collector=(
            SuccessfulBehaviouralCollector()
        ),

        prediction_service=(
            FakePredictionService()
        ),
    )

    response = service.scan(
        "https://example.com"
    )

    assert response.status == (
        "completed"
    )

    assert (
        response.primary_configuration
        == "hybrid"
    )

    assert response.predicted_label == 1

    assert response.predicted_class == (
        "Scam Website"
    )

    assert len(
        repository.results
    ) == 3

    assert repository.committed is True


def test_heuristic_fallback_when_behaviour_fails():

    repository = FakeRepository()

    service = ScanService(
        repository=repository,
        validator=ValidValidator(),

        heuristic_collector=(
            SuccessfulHeuristicCollector()
        ),

        behavioural_collector=(
            FailedBehaviouralCollector()
        ),

        prediction_service=(
            FakePredictionService()
        ),
    )

    response = service.scan(
        "https://example.com"
    )

    assert response.status == (
        "partial"
    )

    assert (
        response.primary_configuration
        == "heuristic_fallback"
    )

    assert response.hybrid_result is None

    assert (
        response.behavioural_result
        is None
    )

    assert len(
        repository.results
    ) == 1


def test_invalid_url_returns_no_prediction():

    repository = FakeRepository()

    service = ScanService(
        repository=repository,
        validator=InvalidValidator(),

        heuristic_collector=(
            SuccessfulHeuristicCollector()
        ),

        behavioural_collector=(
            SuccessfulBehaviouralCollector()
        ),

        prediction_service=(
            FakePredictionService()
        ),
    )

    response = service.scan(
        "not-a-valid-url"
    )

    assert response.status == "failed"

    assert response.predicted_label is None

    assert response.hybrid_result is None

    assert len(
        repository.results
    ) == 0