from typing import Any, Self

from mibig.converters.shared.common import QualityLevel
from mibig.errors import ValidationError, ValidationErrorInfo
from mibig.converters.shared.mibig.common import SubstrateEvidence


class Ketoreductase:
    inactive: bool | None
    stereochemistry: str | None
    evidence: list[SubstrateEvidence] | None

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
        validate: bool = True,
        **kwargs,
    ):
        self.inactive = inactive
        self.stereochemistry = stereochemistry
        self.evidence = evidence

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

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

            for ev in self.evidence:
                errors.extend(ev.validate(**kwargs))

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
        ret: dict[str, Any] = {}
        if self.inactive is not None:
            ret["inactive"] = self.inactive
        if self.stereochemistry is not None:
            ret["stereochemistry"] = self.stereochemistry
        if self.evidence:
            ret["evidence"] = [e.to_json() for e in self.evidence]

        return ret
