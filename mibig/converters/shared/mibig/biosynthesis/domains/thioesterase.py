from typing import Any, Self

from mibig.errors import ValidationError, ValidationErrorInfo


class Thioesterase:
    subtype: str | None = None

    VALID_SUBTYPES = (
        'Type I',
        'Type II',
    )

    def __init__(self, subtype: str | None = None, validate: bool = True):
        self.subtype = subtype

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []

        if self.subtype and self.subtype not in self.VALID_SUBTYPES:
            errors.append(ValidationErrorInfo("Thioesterase.subtype", f"Invalid subtype: {self.subtype}"))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            subtype=raw.get("subtype"),
        )

    def to_json(self) -> dict[str, Any]:
        ret = {}
        if self.subtype:
            ret["subtype"] = self.subtype

        return ret
