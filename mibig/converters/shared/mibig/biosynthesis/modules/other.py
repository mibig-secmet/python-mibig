from typing import Any, Self

from mibig.errors import ValidationError, ValidationErrorInfo

class Other:
    subtype: str

    def __init__(self, subtype: str, validate: bool = True, **kwargs):
        self.subtype = subtype

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **_) -> list[ValidationErrorInfo]:
        errors = []
        if not self.subtype:
            errors.append(ValidationErrorInfo("Other.subtype", "Missing subtype"))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            subtype=raw["subtype"],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "subtype": self.subtype,
        }
