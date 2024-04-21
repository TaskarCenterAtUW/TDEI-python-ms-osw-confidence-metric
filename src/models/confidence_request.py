from dataclasses import dataclass


@dataclass
class RequestData:
    jobId: str
    data_file: str
    meta_file: str
    sub_regions_file: str
    trigger_type: str


@dataclass
class ConfidenceRequest:
    messageType: str
    messageId: str
    data: RequestData

    def __post_init__(self):
        self.data = RequestData(**self.data)
