from typing import Any, Self

from mibig.errors import ValidationError, ValidationErrorInfo

class Other:
    subclass: str
    details: str | None

    VALID_SUBCLASSES = (
        "aminocoumarin",
        "cyclitol",
        "other",
    )

    def __init__(self,
                 subclass: str,
                 details: str | None = None,
                 validate: bool = True) -> None:
        self.subclass = subclass
        self.details = details

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []

        if self.subclass not in self.VALID_SUBCLASSES:
            errors.append(ValidationErrorInfo("Other.subclass", f"Invalid subclass: {self.subclass}"))

        if self.subclass == "other" and not self.details:
            errors.append(ValidationErrorInfo("Other.details", "Missing details for subclass 'other'"))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            subclass=raw["subclass"],
            details=raw.get("details"),
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "subclass": self.subclass,
        }
        if self.details:
            ret["details"] = self.details

        return ret

