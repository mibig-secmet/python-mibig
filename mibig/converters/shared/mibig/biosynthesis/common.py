import re
from typing import Any, Self

from mibig.converters.shared.common import Citation, Smiles, validate_citation_list
from mibig.converters.shared.mibig.common import QualityLevel
from mibig.converters.shared.mibig.compound import VALID_NAME_PATTERN
from mibig.errors import ValidationError, ValidationErrorInfo


class Monomer:
    name: str
    structure: Smiles
    references: list[Citation]

    def __init__(self, name: str, structure: Smiles, references: list[Citation], validate: bool = True):
        self.name = name
        self.structure = structure
        self.references = references

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []

        if not re.match(VALID_NAME_PATTERN, self.name):
            errors.append(ValidationErrorInfo("Monomer.name", f"Invalid name: {self.name}"))

        errors.extend(validate_citation_list(self.references))
        errors.extend(self.structure.validate())
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            name=raw["name"],
            structure=Smiles(raw["structure"]),
            references=[Citation.from_json(ref) for ref in raw["references"]],
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "structure": self.structure.to_json(),
            "references": [ref.to_json() for ref in self.references],
        }


class ReleaseType:
    name: str
    details: str | None
    references: list[Citation]

    VALID_RELEASE_TYPES = (
        "Claisen condensation",
        "Hydrolysis",
        "Macrolactamization",
        "Macrolactonization",
        "None",
        "Other",
        "Reductive release",
    )

    def __init__(self, name: str, references: list[Citation], details: str | None = None, validate: bool = True, **kwargs):
        self.name = name
        self.details = details
        self.references = references

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, quality: QualityLevel | None = None) -> list[ValidationErrorInfo]:
        errors = []
        if self.name not in self.VALID_RELEASE_TYPES:
            errors.append(ValidationErrorInfo("ReleaseType.name", f"Invalid release type: {self.name}"))

        if self.name == "Other" and not self.details:
            errors.append(ValidationErrorInfo("ReleaseType.details", "Details must be provided for 'Other' release types"))

        if quality and quality is not QualityLevel.QUESTIONABLE:
            errors.extend(validate_citation_list(self.references))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            name=raw["name"],
            details=raw.get("details"),
            references=[Citation.from_json(ref) for ref in raw["references"]],
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "name": self.name,
            "references": [ref.to_json() for ref in self.references],
        }
        if self.details:
            ret["details"] = self.details
        return ret
