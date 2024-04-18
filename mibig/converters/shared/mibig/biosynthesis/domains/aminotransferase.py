from typing import Any, Self

from mibig.converters.shared.common import Citation, validate_citation_list
from mibig.errors import ValidationError, ValidationErrorInfo

class Aminotransferase:
    inactive: bool | None = None
    references: list[Citation]

    def __init__(self, inactive: bool | None = None, references: list[Citation] | None = None, validate: bool = True) -> None:
        self.inactive = inactive
        self.references = references or []

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []
        errors.extend(validate_citation_list(self.references))
        if self.inactive and not self.references:
            errors.append(ValidationErrorInfo("Aminotransferase.evidence", "References are required if inactive is set"))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            inactive=raw.get("inactive"),
            references=[Citation.from_json(ref) for ref in raw.get("references", [])],
        )

    def to_json(self) -> dict[str, Any]:
        ret = {}
        if self.inactive is not None:
            ret["inactive"] = self.inactive
        if self.references:
            ret["references"] = [ref.to_json() for ref in self.references]
        return ret
