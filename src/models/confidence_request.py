from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RequestData:
    jobId: str
    data_file: str
    meta_file: str
    trigger_type: str
    sub_regions_file: Optional[str] = None


@dataclass
class ConfidenceRequest:
    messageType: str
    messageId: str
    data: RequestData

    def __post_init__(self):
        self.data = RequestData(**self.data)
