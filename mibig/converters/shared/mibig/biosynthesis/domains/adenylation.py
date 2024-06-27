from typing import Any, Self

from mibig.converters.shared.common import GeneId, QualityLevel, Smiles
from mibig.converters.shared.mibig.common import SubstrateEvidence
from mibig.errors import ValidationErrorInfo

from .core import ActiveDomain, Substrate

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


class AdenylationSubstrate(Substrate):
    proteinogenic: bool

    def __init__(
        self,
        name: str,
        proteinogenic: bool,
        structure: Smiles | None,
        **kwargs,
    ) -> None:
        self.proteinogenic = proteinogenic
        super().__init__(name, structure, **kwargs)

        if self.proteinogenic and not self.structure:
            self.structure = Smiles(PROTEINOGENIC_SUBSTRATES[self.name.lower()])

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = super().validate(**kwargs)

        if self.proteinogenic and self.name.lower() not in PROTEINOGENIC_SUBSTRATES:
            errors.append(
                ValidationErrorInfo(
                    "AdenylationSubstrate.name",
                    f"Invalid proteinogenic substrate {self.name}",
                )
            )

        if self.structure:
            errors.extend(self.structure.validate(**kwargs))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            name=raw["name"],
            proteinogenic=raw["proteinogenic"],
            structure=Smiles(raw["structure"]) if "structure" in raw else None,
        )

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret.update({
            "proteinogenic": self.proteinogenic,
        })
        return ret

    def __repr__(self) -> str:
        return f"<AdenylationSubstrate {self.name}>"


class Adenylation(ActiveDomain):
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
        **kwargs,
    ) -> None:
        self.precursor_biosynthesis = precursor_biosynthesis

        super().__init__(active=None if inactive is None else not inactive, evidence=evidence,
                         substrates=substrates, **kwargs)

    def validate(
        self, quality: QualityLevel | None = None, **kwargs
    ) -> list[ValidationErrorInfo]:
        errors = super().validate(quality=quality, **kwargs)
        if self.substrates:
            if not self.evidence and quality != QualityLevel.QUESTIONABLE:
                errors.append(
                    ValidationErrorInfo(
                        "Adenylation.evidence", "Evidence is required for adenylation"
                    )
                )
        if self.active is False:
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
                AdenylationSubstrate.from_json(sub) for sub in raw.get("substrates", [])
            ],
            evidence=[
                SubstrateEvidence.from_json(ev, **kwargs) for ev in raw.get("evidence", [])
            ],
            precursor_biosynthesis=[
                GeneId.from_json(gene, **kwargs)
                for gene in raw.get("precursor_biosynthesis", [])
            ],
            inactive=raw.get("inactive"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.precursor_biosynthesis:
            ret["precursor_biosynthesis"] = [
                gene.to_json() for gene in self.precursor_biosynthesis
            ]
        if self.active is not None:
            ret.pop("active")
            ret["inactive"] = not self.active

        return ret
