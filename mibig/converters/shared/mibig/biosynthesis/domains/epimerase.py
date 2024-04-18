from typing import Any, Self

from mibig.errors import ValidationErrorInfo

class Epimerase:
    def __init__(self):
        pass

    def validate(self) -> list[ValidationErrorInfo]:
        return []

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        _ = raw
        return cls()

    def to_json(self) -> dict[str, Any]:
        return {}

