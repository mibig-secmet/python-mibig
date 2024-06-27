from typing import Any, Self

from mibig.errors import ValidationErrorInfo

from .core import DomainInfo


class Methyltransferase(DomainInfo):
    details: str | None

    VALID_SUBTYPES = (
        'C',
        'N',
        'O',
        'other',
    )

    def __init__(self, subtype: str | None = None, details: str | None = None, **kwargs):
        self.details = details
        super().__init__(subtype=subtype, **kwargs)

    def validate(self, **_) -> list[ValidationErrorInfo]:
        errors = []

        if self.subtype == 'other' and not self.details:
            errors.append(ValidationErrorInfo("Methyltransferase.details", "Missing required details for subtype 'other'"))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            subtype=raw.get("subtype"),
            details=raw.get("details"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.details:
            ret["details"] = self.details

        return ret
