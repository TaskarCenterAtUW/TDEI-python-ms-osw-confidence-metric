from dataclasses import dataclass

@dataclass
class ConfidenceRequested():
    jobId: str
    data_file:str
    meta_file:str
    trigger_type:str