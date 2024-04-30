from typing import Any, Self

from mibig.converters.shared.common import QualityLevel, Smiles
from mibig.converters.shared.mibig.common import SubstrateEvidence
from mibig.errors import ValidationError, ValidationErrorInfo

class Ligase:
    substrates: list[Smiles]
    evidence: list[SubstrateEvidence]

    def __init__(self, substrates: list[Smiles], evidence: list[SubstrateEvidence], validate: bool = True, **kwargs) -> None:
        self.substrates = substrates
        self.evidence = evidence

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, quality: QualityLevel | None = None, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        for substrate in self.substrates:
            errors.extend(substrate.validate())
        if quality != QualityLevel.QUESTIONABLE:
            if self.substrates and not self.evidence:
                errors.append(ValidationErrorInfo("Ligase", "Ligase has substrates but no evidence"))
        for evidence in self.evidence:
            errors.extend(evidence.validate())
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            substrates=[Smiles(sub) for sub in raw.get("substrates", [])],
            evidence=[SubstrateEvidence.from_json(evi) for evi in raw.get("evidence", [])],
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "substrates": [sub.to_json() for sub in self.substrates],
            "evidence": [evi.to_json() for evi in self.evidence],
        }
        return ret
