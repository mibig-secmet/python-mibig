from typing import Any, Self

from mibig.errors import ValidationError, ValidationErrorInfo

class Other:
    subtype: str
    active: bool | None

    def __init__(self, subtype: str, active: bool | None = None, validate: bool = True):
        self.subtype = subtype
        self.active = active

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []
        if not self.subtype:
            errors.append(ValidationErrorInfo("Other.subtype", "Missing required subtype"))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            subtype=raw["subtype"],
            active=raw.get("active"),
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "subtype": self.subtype,
        }
        if self.active is not None:
            ret["active"] = self.active

        return ret

