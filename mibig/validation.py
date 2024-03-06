from dataclasses import dataclass

@dataclass
class ValidationErrorInfo:
    field: str
    message: str



