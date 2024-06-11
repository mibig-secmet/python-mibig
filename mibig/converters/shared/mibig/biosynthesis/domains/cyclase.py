from typing import Any, Self

from mibig.converters.shared.common import Citation, QualityLevel, validate_citation_list
from mibig.errors import ValidationError, ValidationErrorInfo


class Cyclase:
    references: list[Citation]

    def __init__(self, references: list[Citation], validate: bool = True, **kwargs):
        self.references = references

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        quality: QualityLevel | None = kwargs.get("quality")
        errors.extend(validate_citation_list(self.references, "Cyclase.references", quality=quality))

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
