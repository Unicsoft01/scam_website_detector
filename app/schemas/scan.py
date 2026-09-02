from dataclasses import dataclass
from typing import Optional


@dataclass
class ModelDecision:
    configuration: str
    scam_probability: float
    threshold: float
    predicted_label: int
    predicted_class: str
    model_version: str


@dataclass
class ScanResponse:
    scan_id: int
    submitted_url: str
    normalized_url: Optional[str]

    status: str

    behavioural_available: Optional[bool]

    primary_configuration: Optional[str]

    predicted_label: Optional[int]
    predicted_class: Optional[str]
    scam_probability: Optional[float]

    heuristic_result: Optional[ModelDecision]
    behavioural_result: Optional[ModelDecision]
    hybrid_result: Optional[ModelDecision]

    message: str

    configuration: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None