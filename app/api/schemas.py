from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class ScanRequest(BaseModel):

    url: str = Field(
        ...,
        min_length=3,
        max_length=4096,
        description=(
            "HTTP or HTTPS website URL "
            "to be analysed."
        ),
        examples=[
            "https://example.com"
        ],
    )

    @field_validator("url")
    @classmethod
    def clean_url(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:

            raise ValueError(
                "URL cannot be empty."
            )

        return value


class ModelResultResponse(BaseModel):

    configuration: str

    scam_probability: float = Field(
        ge=0.0,
        le=1.0,
    )

    threshold_used: float = Field(
        ge=0.0,
        le=1.0,
    )

    predicted_label: int = Field(
        ge=0,
        le=1,
    )

    predicted_class: str

    model_version: Optional[str] = None

    response_time_ms: Optional[float] = None


class ScanSubmissionResponse(BaseModel):

    scan_id: int

    submitted_url: str

    normalized_url: Optional[str] = None

    status: str

    behavioural_available: Optional[
        bool
    ] = None

    primary_configuration: Optional[
        str
    ] = None

    predicted_label: Optional[
        int
    ] = None

    predicted_class: Optional[
        str
    ] = None

    scam_probability: Optional[
        float
    ] = None

    message: str


class ScanResultResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    scan_id: int

    submitted_url: str

    normalized_url: str

    registrable_domain: Optional[str]

    scan_status: str

    behavioural_available: Optional[
        bool
    ]

    initiated_at: datetime

    completed_at: Optional[datetime]

    error_code: Optional[str]

    error_message: Optional[str]

    results: list[
        ModelResultResponse
    ] = []


class ScanHistoryItem(BaseModel):

    scan_id: int

    submitted_url: str

    normalized_url: str

    registrable_domain: Optional[str]

    scan_status: str

    behavioural_available: Optional[
        bool
    ]

    initiated_at: datetime

    completed_at: Optional[datetime]


class ScanHistoryResponse(BaseModel):

    total: int

    limit: int

    offset: int

    scans: list[
        ScanHistoryItem
    ]


class HealthResponse(BaseModel):

    status: str

    application: str

    database: str