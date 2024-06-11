from typing import Any, Self

from mibig.errors import ValidationError, ValidationErrorInfo

class Methyltransferase:
    subtype: str | None
    details: str | None

    VALID_SUBTYPES = (
        'C',
        'N',
        'O',
        'other',
    )

    def __init__(self, subtype: str | None = None, details: str | None = None, validate: bool = True, **kwargs):
        self.subtype = subtype
        self.details = details

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **_) -> list[ValidationErrorInfo]:
        errors = []

        if self.subtype and self.subtype not in self.VALID_SUBTYPES:
            errors.append(ValidationErrorInfo("Methyltransferase.subtype", f"Invalid subtype: {self.subtype}"))

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
        ret: dict[str, Any] = {}
        if self.subtype:
            ret["subtype"] = self.subtype
        if self.details:
            ret["details"] = self.details

        return ret



