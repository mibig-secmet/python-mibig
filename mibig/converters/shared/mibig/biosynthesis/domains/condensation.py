from typing import Any, Self

from mibig.converters.shared.common import Citation
from mibig.errors import ValidationError, ValidationErrorInfo

class Condensation:
    subtype: str | None
    references: list[Citation]

    VALID_SUBTYPES = (
        "Dual",
        "Starter",
        "LCL",
        "DCL",
        "Ester bond-forming",
        "Heterocyclization",
    )

    def __init__(self, subtype: str | None, references: list[Citation], validate: bool = True):
        self.subtype = subtype
        self.references = references

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []

        if self.subtype and self.subtype not in self.VALID_SUBTYPES:
            errors.append(ValidationErrorInfo("Condensation.subtype", f"Invalid subtype: {self.subtype}"))

        for ref in self.references:
            errors.extend(ref.validate())
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            subtype=raw.get("subtype"),
            references=[Citation.from_json(ref) for ref in raw.get("references", [])],
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
        }

        if self.subtype:
            ret["subtype"] = self.subtype

        if self.references:
            ret["references"] = [ref.to_json() for ref in self.references]

        return ret
