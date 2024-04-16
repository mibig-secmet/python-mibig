from typing import Any, Self

from mibig.converters.shared.common import Location, Smiles
from mibig.converters.shared.mibig.common import SubstrateEvidence
from mibig.errors import ValidationError, ValidationErrorInfo

class Substrate:
    evidence: list[SubstrateEvidence]
    structure: Smiles
    name: str | None

    def __init__(self, evidence: list[SubstrateEvidence], structure: Smiles, name: str | None, validate: bool = True):
        self.evidence = evidence
        self.structure = structure
        self.name = name

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []
        errors.extend(self.structure.validate())

        if not self.evidence:
            errors.append(ValidationErrorInfo("Substrate.evidence", "At least one evidence is required"))

        for evidence in self.evidence:
            errors.extend(evidence.validate())

        return errors

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            [SubstrateEvidence.from_json(evidence) for evidence in data["evidence"]],
            Smiles.from_json(data["structure"]),
            data.get("name"),
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "evidence": [evidence.to_json() for evidence in self.evidence],
            "structure": self.structure.to_json(),
            "name": self.name,
        }


class Domain:
    location: Location
    name: str
    substrate: list[Substrate] | None

    def __init__(self, location: Location, name: str, substrate: list[Substrate] | None = None, validate: bool = True):
        self.location = location
        self.name = name
        self.substrate = substrate

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []
        errors.extend(self.location.validate())

        if not self.substrate:
            return errors

        for substrate in self.substrate:
            errors.extend(substrate.validate())

        return errors

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        return cls(
            Location.from_json(data["location"]),
            data["name"],
            [Substrate.from_json(sub) for sub in data.get("substrate", [])],
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "location": self.location.to_json(),
            "name": self.name,
            "substrate": [sub.to_json() for sub in self.substrate] if self.substrate else None,
        }
