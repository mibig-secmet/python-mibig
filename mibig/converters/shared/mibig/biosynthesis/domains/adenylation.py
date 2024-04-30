from typing import Any, Self

from mibig.converters.shared.common import GeneId, QualityLevel, Smiles
from mibig.converters.shared.mibig.common import SubstrateEvidence
from mibig.errors import ValidationError, ValidationErrorInfo

PROTEINOGENIC_SUBSTRATES = {
    "alanine": "NC(C)C(=O)O",
    "arginine": "NC(CCCNC(N)=N)C(=O)O",
    "asparagine": "NC(CC(=O)N)C(=O)O",
    "aspartic acid": "NC(CC(=O)O)C(=O)O",
    "cysteine": "NC(CS)C(=O)O",
    "glutamine": "NC(CCC(=O)N)C(=O)O",
    "glutamic acid": "NC(CCC(=O)O)C(=O)O",
    "glycine": "NCC(=O)O",
    "histidine": "NC(CC1=CNC=N1)C(=O)O",
    "isoleucine": "NC(C(C)CC)C(=O)O",
    "leucine": "NC(CC(C)C)C(=O)O",
    "lysine": "NC(CCCCN)C(=O)O",
    "methionine": "NC(CCSC)C(=O)O",
    "phenylalanine": "NC(Cc1ccccc1)C(=O)O",
    "proline": "N1C(CCC1)C(=O)O",
    "serine": "NC(CO)C(=O)O",
    "threonine": "NC(C(O)C)C(=O)O",
    "tryptophan": "NC(CC1=CNc2c1cccc2)C(=O)O",
    "tyrosine": "NC(Cc1ccc(O)cc1)C(=O)O",
    "valine": "NC(C(C)C)C(=O)O",
}


class AdenylationSubstrate:
    name: str
    proteinogenic: bool
    structure: Smiles | None

    def __init__(
        self,
        name: str,
        proteinogenic: bool,
        structure: Smiles | None,
        validate: bool = True,
    ) -> None:
        self.name = name
        self.proteinogenic = proteinogenic
        self.structure = structure

        if self.proteinogenic and not self.structure:
            self.structure = Smiles(PROTEINOGENIC_SUBSTRATES[self.name.lower()])

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []

        if not self.name:
            errors.append(
                ValidationErrorInfo("AdenylationSubstrate.name", "Missing name")
            )

        if self.proteinogenic and self.name.lower() not in PROTEINOGENIC_SUBSTRATES:
            errors.append(
                ValidationErrorInfo(
                    "AdenylationSubstrate.name",
                    f"Invalid proteinogenic substrate {self.name}",
                )
            )

        if self.structure:
            errors.extend(self.structure.validate())

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            name=raw["name"],
            proteinogenic=raw["proteinogenic"],
            structure=Smiles(raw["structure"]) if "structure" in raw else None,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "name": self.name,
            "proteinogenic": self.proteinogenic,
        }
        if self.structure:
            ret["structure"] = self.structure.to_json()

        return ret

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<AdenylationSubstrate {self.name}>"


class Adenylation:
    substrates: list[AdenylationSubstrate]
    evidence: list[SubstrateEvidence]
    precursor_biosynthesis: list[GeneId]
    inactive: bool | None = None

    def __init__(
        self,
        substrates: list[AdenylationSubstrate],
        evidence: list[SubstrateEvidence],
        precursor_biosynthesis: list[GeneId],
        inactive: bool | None = None,
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.substrates = substrates
        self.evidence = evidence
        self.precursor_biosynthesis = precursor_biosynthesis
        self.inactive = inactive

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(
        self, quality: QualityLevel | None = None, **kwargs
    ) -> list[ValidationErrorInfo]:
        errors = []
        for substrate in self.substrates:
            errors.extend(substrate.validate(**kwargs))
        for gene in self.precursor_biosynthesis:
            errors.extend(gene.validate(**kwargs))
        for ev in self.evidence:
            errors.extend(ev.validate(quality=quality, **kwargs))
        if self.substrates:
            if not self.evidence and quality != QualityLevel.QUESTIONABLE:
                print(self.substrates)
                errors.append(
                    ValidationErrorInfo(
                        "Adenylation.evidence", "Evidence is required for adenylation"
                    )
                )
        if self.inactive:
            if self.substrates:
                errors.append(
                    ValidationErrorInfo(
                        "Adenylation.inactive",
                        "Inactive adenylation domains cannot have a substrate",
                    )
                )
            if not self.evidence:
                errors.append(
                    ValidationErrorInfo(
                        "Adenylation.evidence",
                        "Evidence is required for inactive adenylation domains",
                    )
                )
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            substrates=[
                AdenylationSubstrate.from_json(sub) for sub in raw["substrates"]
            ],
            evidence=[
                SubstrateEvidence.from_json(ev) for ev in raw.get("evidence", [])
            ],
            precursor_biosynthesis=[
                GeneId.from_json(gene, **kwargs)
                for gene in raw.get("precursor_biosynthesis", [])
            ],
            inactive=raw.get("inactive"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {}
        if self.substrates:
            ret["substrates"] = [sub.to_json() for sub in self.substrates]
        if self.evidence:
            ret["evidence"] = [ev.to_json() for ev in self.evidence]
        if self.precursor_biosynthesis:
            ret["precursor_biosynthesis"] = [
                gene.to_json() for gene in self.precursor_biosynthesis
            ]
        if self.inactive:
            ret["inactive"] = self.inactive

        return ret
