from typing import Any, Self

from mibig.converters.shared.common import Citation
from mibig.errors import ValidationError, ValidationErrorInfo


class Cyclase:
    references: list[Citation]

    def __init__(self, references: list[Citation], validate: bool = True):
        self.references = references

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []
        for ref in self.references:
            errors.extend(ref.validate())

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            references=[Citation.from_json(ref) for ref in raw.get("references", [])],
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
        }

        if self.references:
            ret["references"] = [ref.to_json() for ref in self.references]

        return ret
