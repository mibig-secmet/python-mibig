from typing import Any, Self

from mibig.errors import ValidationError, ValidationErrorInfo

class ProductTemplate:
    active: bool | None

    def __init__(self, active: bool | None = None, validate: bool = True, **kwargs):
        self.active = active

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **_) -> list[ValidationErrorInfo]:
        errors = []

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            active=raw.get("active"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
        }
        if self.active is not None:
            ret["active"] = self.active

        return ret


