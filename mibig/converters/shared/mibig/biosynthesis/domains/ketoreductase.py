from typing import Any, Self

from mibig.errors import ValidationError, ValidationErrorInfo
from mibig.converters.shared.mibig.common import SubstrateEvidence

class Ketoreductase:
    inactive: bool | None
    stereochemistry: str | None
    evidence: list[SubstrateEvidence] | None

    VALID_STEREOCHEMISTRY = (
        "A1",
        "A2",
        "B1",
        "B2",
        "C1",
        "C2",
    )

    def __init__(self, inactive: bool | None = None, stereochemistry: str | None = None,
                 evidence: list[SubstrateEvidence] | None = None, validate: bool = True):
        self.inactive = inactive
        self.stereochemistry = stereochemistry
        self.evidence = evidence

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []

        if self.stereochemistry not in self.VALID_STEREOCHEMISTRY:
            errors.append(
                ValidationErrorInfo(
                    field="stereochemistry",
                    message=f"Invalid stereochemistry: {self.stereochemistry}",
                )
            )

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            inactive=raw.get("inactive"),
            stereochemistry=raw.get("stereochemistry"),
            evidence=[SubstrateEvidence.from_json(e) for e in raw.get("evidence", [])],
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {}
        if self.inactive is not None:
            ret["inactive"] = self.inactive
        if self.stereochemistry is not None:
            ret["stereochemistry"] = self.stereochemistry
        if self.evidence:
            ret["evidence"] = [e.to_json() for e in self.evidence]

        return ret
