from typing import Any, Self

from mibig.converters.shared.common import QualityLevel
from mibig.errors import ValidationErrorInfo
from mibig.converters.shared.mibig.common import SubstrateEvidence

from .core import ActiveDomain


class Ketoreductase(ActiveDomain):
    stereochemistry: str | None

    VALID_STEREOCHEMISTRY = (
        "A",
        "B",
        "A1",
        "A2",
        "B1",
        "B2",
        "C1",
        "C2",
    )

    def __init__(
        self,
        inactive: bool | None = None,
        stereochemistry: str | None = None,
        evidence: list[SubstrateEvidence] | None = None,
        **kwargs,
    ):
        self.stereochemistry = stereochemistry
        super().__init__(active=None if inactive is None else not inactive, evidence=evidence, **kwargs)

    def validate(
        self, quality: QualityLevel | None = None, **kwargs
    ) -> list[ValidationErrorInfo]:
        errors = []

        if (
            self.stereochemistry
            and self.stereochemistry not in self.VALID_STEREOCHEMISTRY
        ):
            errors.append(
                ValidationErrorInfo(
                    field="stereochemistry",
                    message=f"Invalid stereochemistry: {self.stereochemistry}",
                )
            )

        if quality != QualityLevel.QUESTIONABLE:
            if not self.evidence:
                errors.append(
                    ValidationErrorInfo(
                        field="evidence",
                        message="Evidence is required for non-questionable quality entries",
                    )
                )
                return errors
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            inactive=raw.get("inactive"),
            stereochemistry=raw.get("stereochemistry"),
            evidence=[SubstrateEvidence.from_json(e) for e in raw.get("evidence", [])],
            **kwargs
        )

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.active is not None:
            ret["inactive"] = not ret.pop("active")
        if self.stereochemistry is not None:
            ret["stereochemistry"] = self.stereochemistry

        return ret
