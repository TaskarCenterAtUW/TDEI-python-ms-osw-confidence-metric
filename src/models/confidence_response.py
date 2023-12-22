from dataclasses import dataclass


@dataclass
class ConfidenceResponse:
    jobId: str
    confidence_level: float
    confidence_library_version: str
    status: str
    message: str
    success: bool
