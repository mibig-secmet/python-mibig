from enum import Enum
from typing import Any, Self

from mibig.converters.shared.common import Citation, GeneId, validate_citation_list
from mibig.converters.shared.mibig.biosynthesis.common import Monomer
from mibig.errors import ValidationError, ValidationErrorInfo

from .cal import CAL
from .nrps import NrpsTypeI
from .other import Other
from .pks import PksIterative, PksModular, PksTransAt

ExtraInfo = CAL | NrpsTypeI | Other | PksIterative | PksModular | PksTransAt

class NcaEvidence:
    method: str
    references: list[Citation]

    VALID_METHODS = (
        "Sequence-based prediction",
        "Structure-based inference",
        "Activity assay",
    )

    def __init__(self, method: str, references: list[Citation], validate: bool = True) -> None:
        self.method = method
        self.references = references

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []

        if self.method not in self.VALID_METHODS:
            errors.append(ValidationErrorInfo("NcaEvidence.method", f"Invalid method {self.method}"))

        errors.extend(validate_citation_list(self.references))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        refs = [Citation.from_json(c) for c in raw["references"]]
        return cls(raw["method"], refs)

    def to_json(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "references": [r.to_json() for r in self.references]
        }


class NonCanonicalActivity:
    evidence: list[NcaEvidence]
    iterations: int | None = None
    non_elongating: bool | None = None
    skipped: bool | None = None

    def __init__(self, evidence: list[NcaEvidence], iterations: int | None = None, non_elongating: bool | None = None,
                 skipped: bool | None = None, validate: bool = True) -> None:
        self.evidence = evidence
        self.iterations = iterations
        self.non_elongating = non_elongating
        self.skipped = skipped

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []

        for evidence in self.evidence:
            errors.extend(evidence.validate())

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            evidence=[NcaEvidence.from_json(evidence) for evidence in raw["evidence"]],
            iterations=raw.get("iterations"),
            non_elongating=raw.get("nonElongating"),
            skipped=raw.get("skipped"),
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "evidence": [evidence.to_json() for evidence in self.evidence],
        }
        if self.iterations is not None:
            ret["iterations"] = self.iterations
        if self.non_elongating is not None:
            ret["nonElongating"] = self.non_elongating
        if self.skipped is not None:
            ret["skipped"] = self.skipped
        return ret



class ModuleType(Enum):
    CAL = "cal"
    NRPS_TYPE1 = "nrps-type1"
    NRPS_TYPE6 = "nrps-type6"
    OTHER = "other"
    PKS_ITERATIVE = "pks-iterative"
    PKS_MODULAR = "pks-modular"
    PKS_TRANS_AT = "pks-trans-at"


MAPPING = {
    ModuleType.CAL: CAL,
    ModuleType.NRPS_TYPE1: NrpsTypeI,
    ModuleType.NRPS_TYPE6: NrpsTypeI,  # There's basically no difference between the two
    ModuleType.OTHER: Other,
    ModuleType.PKS_ITERATIVE: PksIterative,
    ModuleType.PKS_MODULAR: PksModular,
    ModuleType.PKS_TRANS_AT: PksTransAt,
}


class Module:
    module_type: str
    name: str
    genes: list[GeneId]
    active: bool
    extra_info: ExtraInfo
    integrated_monomers: list[Monomer]
    comment: str | None

    def __init__(self, module_type: str, name: str, genes: list[GeneId], active: bool, extra_info: ExtraInfo,
                 integrated_monomers: list[Monomer], comment: str | None = None, validate: bool = True, **kwargs) -> None:
        self.module_type = module_type
        self.name = name
        self.genes = genes
        self.active = active
        self.extra_info = extra_info
        self.integrated_monomers = integrated_monomers
        self.comment = comment

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []

        errors.extend(self.extra_info.validate(**kwargs))

        for monomer in self.integrated_monomers:
            errors.extend(monomer.validate())

        for gene in self.genes:
            errors.extend(gene.validate(record=kwargs.get("record")))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        module_type = raw["type"]
        extra_info = MAPPING[ModuleType(module_type)].from_json(raw, **kwargs)

        return cls(
            module_type=module_type,
            name=raw["name"],
            genes=[GeneId.from_json(gene, **kwargs) for gene in raw["genes"]],
            active=raw["active"],
            extra_info=extra_info,
            comment=raw.get("comment"),
            integrated_monomers=[Monomer.from_json(monomer) for monomer in raw.get("integrated_monomers", [])],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "type": self.module_type,
            "name": self.name,
            "genes": [gene.to_json() for gene in self.genes],
            "active": self.active,
            **self.extra_info.to_json(),
        }
        if self.integrated_monomers:
            ret["integrated_monomers"] = [monomer.to_json() for monomer in self.integrated_monomers]

        if self.comment:
            ret["comment"] = self.comment

        return ret
