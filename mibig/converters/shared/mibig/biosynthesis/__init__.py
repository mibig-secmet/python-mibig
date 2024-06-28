from typing import Any, Self

from mibig.converters.shared.common import Citation, GeneId, QualityLevel, validate_citation_list
from mibig.converters.shared.mibig.biosynthesis.classes import BiosynthesisClass
from mibig.converters.shared.mibig.biosynthesis.modules.base import Module
from mibig.converters.shared.mibig.biosynthesis.path import Path
from mibig.errors import ValidationError, ValidationErrorInfo


class OperonEvidence:
    method: str
    references: list[Citation]

    VALID_METHODS = {
        "Sequence-based prediction",
        "RACE",
        "ChIPseq",
        "RNAseq",
        "rt-PCR",
    }

    def __init__(
        self, method: str, references: list[Citation], validate: bool = True, **kwargs
    ) -> None:
        self.method = method
        self.references = references

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []

        quality: QualityLevel | None = kwargs.get("quality")

        if self.method not in self.VALID_METHODS:
            errors.append(
                ValidationErrorInfo(
                    "OperonEvidence.method", f"Invalid method: {self.method}"
                )
            )

        if quality != QualityLevel.QUESTIONABLE:
            errors.extend(
                validate_citation_list(self.references, "OperonEvidence.references")
            )
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            method=raw["method"],
            references=[Citation.from_json(ref) for ref in raw["references"]],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "references": [ref.to_json() for ref in self.references],
        }


class Operon:
    genes: list[GeneId]
    evidence: list[OperonEvidence]

    def __init__(
        self,
        genes: list[GeneId],
        evidence: list[OperonEvidence],
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.genes = genes
        self.evidence = evidence

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []

        for gene in self.genes:
            errors.extend(gene.validate(**kwargs))

        for evidence in self.evidence:
            errors.extend(evidence.validate(**kwargs))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            genes=[GeneId.from_json(gene, **kwargs) for gene in raw["genes"]],
            evidence=[
                OperonEvidence.from_json(evidence, **kwargs) for evidence in raw["evidence"]
            ],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "genes": [gene.to_json() for gene in self.genes],
            "evidence": [evidence.to_json() for evidence in self.evidence],
        }


class Biosynthesis:
    classes: list[BiosynthesisClass]
    modules: list[Module]
    operons: list[Operon]
    paths: list[Path]

    def __init__(
        self,
        classes: list[BiosynthesisClass],
        modules: list[Module],
        operons: list[Operon],
        paths: list[Path],
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.classes = classes
        self.modules = modules
        self.operons = operons
        self.paths = paths

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(
        self, quality: QualityLevel | None = None, **kwargs
    ) -> list[ValidationErrorInfo]:
        errors = []
        if not self.classes:
            errors.append(
                ValidationErrorInfo(
                    "Biosynthesis.classes", "At least one class is required"
                )
            )

        if quality and quality is not QualityLevel.QUESTIONABLE:
            if False and not self.paths:  # TODO
                errors.append(
                    ValidationErrorInfo(
                        "Biosynthesis.paths", "At least one path is required"
                    )
                )

        for _class in self.classes:
            errors.extend(_class.validate(quality=quality, **kwargs))
        for module in self.modules:
            errors.extend(module.validate(quality=quality, **kwargs))
        for operon in self.operons:
            errors.extend(operon.validate(quality=quality, **kwargs))
        for path in self.paths:
            errors.extend(path.validate())
        return errors

    @property
    def genes_referenced(self) -> list[GeneId]:
        genes = set()
        for module in self.modules:
            genes.update(module.genes)
        for operon in self.operons:
            genes.update(operon.genes)
        return sorted(list(genes))

    @property
    def references(self) -> list[Citation]:
        references = set()
        for _class in self.classes:
            references.update(_class.references)
        for operon in self.operons:
            for evidence in operon.evidence:
                references.update(evidence.references)
        for module in self.modules:
            references.update(module.references)
        for path in self.paths:
            references.update(path.references)
        return sorted(list(references))

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            classes=[BiosynthesisClass.from_json(cls, **kwargs) for cls in raw["classes"]],
            modules=[
                Module.from_json(module, **kwargs) for module in raw.get("modules", [])
            ],
            operons=[
                Operon.from_json(operons, **kwargs)
                for operons in raw.get("operons", [])
            ],
            paths=[Path.from_json(path) for path in raw.get("paths", [])],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "classes": [cls.to_json() for cls in self.classes],
        }

        if self.modules:
            ret["modules"] = [module.to_json() for module in self.modules]

        if self.operons:
            ret["operons"] = [operon.to_json() for operon in self.operons]

        if self.paths:
            ret["paths"] = [path.to_json() for path in self.paths]

        return ret
