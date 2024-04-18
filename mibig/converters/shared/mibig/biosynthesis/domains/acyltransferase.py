from typing import Any, Self

from mibig.converters.shared.common import Smiles
from mibig.converters.shared.mibig.common import SubstrateEvidence
from mibig.errors import ValidationError, ValidationErrorInfo


class ATSubstrate:
    name: str
    details: str | None = None
    structure: Smiles | None = None

    VALID_NAMES = (
        "malonyl-CoA",
        "methylmalonyl-CoA",
        "ethylmalonyl-CoA",
        "other",
    )

    def __init__(
        self,
        name: str,
        details: str | None = None,
        structure: Smiles | None = None,
        validate: bool = True,
    ) -> None:
        self.name = name
        self.details = details
        self.structure = structure

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []
        if self.name not in self.VALID_NAMES:
            errors.append(
                ValidationErrorInfo("ATSubstrate.name", f"Invalid substrate name: {self.name}")
            )

        if self.name == "other":
            if not self.details:
                errors.append(
                    ValidationErrorInfo(
                        "ATSubstrate.details", "Details are required for 'other' substrate"
                    )
                )

            if not self.structure:
                errors.append(
                    ValidationErrorInfo(
                        "ATSubstrate.structure", "Structure is required for 'other' substrate"
                    )
                )

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            name=raw["name"],
            details=raw.get("details"),
            structure=Smiles.from_json(raw.get("structure", "")),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "name": self.name,
        }
        if self.details:
            ret["details"] = self.details
        if self.structure:
            ret["structure"] = self.structure.to_json()
        return ret




class Acyltransferase:
    subtype: str | None = None
    substrates: list[ATSubstrate]
    evidence: list[SubstrateEvidence]
    inactive: bool | None = None

    VALID_SUBTYPES = (
        "cis-AT",
        "trans-AT",
    )

    def __init__(self, substrates: list[ATSubstrate], evidence: list[SubstrateEvidence], inactive: bool | None = None, validate: bool = True, **kwargs) -> None:
        self.substrates = substrates
        self.evidence = evidence
        self.inactive = inactive

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        for substrate in self.substrates:
            errors.extend(substrate.validate())
        for ev in self.evidence:
            errors.extend(ev.validate(**kwargs))
        if self.substrates and not self.evidence:
            errors.append(ValidationErrorInfo("Acyltransferase.evidence", "Evidence is required if substrates are present"))
        if self.inactive:
            if not self.evidence:
                errors.append(ValidationErrorInfo("Acyltransferase.evidence", "Evidence is required if inactive"))
            if self.substrates:
                errors.append(ValidationErrorInfo("Acyltransferase", "Substrates are not allowed if inactive"))

        if self.subtype and self.subtype not in self.VALID_SUBTYPES:
            errors.append(
                ValidationErrorInfo("Acyltransferase.subtype", f"Invalid subtype: {self.subtype}")
            )
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            substrates=[ATSubstrate.from_json(sub) for sub in raw["substrates"]],
            evidence=[SubstrateEvidence.from_json(ev) for ev in raw["evidence"]],
            inactive=raw.get("inactive"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "substrates": [sub.to_json() for sub in self.substrates],
            "evidence": [ev.to_json() for ev in self.evidence],
        }
        if self.subtype:
            ret["subtype"] = self.subtype
        if self.inactive:
            ret["inactive"] = self.inactive
        return ret
