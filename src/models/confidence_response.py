from dataclasses import dataclass


@dataclass
class ResponseData:
    jobId: str
    confidence_scores: dict
    confidence_library_version: str
    status: str
    message: str
    success: bool

@dataclass
class ConfidenceResponse:
    messageType: str
    messageId: str
    data: ResponseData

    def __post_init__(self):
        self.data = ResponseData(**self.data)
