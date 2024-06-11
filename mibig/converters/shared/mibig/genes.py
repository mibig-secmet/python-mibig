import re
from typing import Any, Self

from mibig.converters.shared.common import (
    Citation,
    GeneId,
    Location,
    NovelGeneId,
    QualityLevel,
    validate_citation_list,
)
from mibig.converters.shared.mibig.biosynthesis.domains.base import Domain
from mibig.converters.shared.mibig.gene.function import GeneFunction, MutationPhenotype
from mibig.errors import ValidationError, ValidationErrorInfo


class GeneLocation:
    exons: list[Location]
    strand: int

    def __init__(
        self, exons: list[Location], strand: int, validate: bool = True, **kwargs
    ):
        self.exons = exons
        self.strand = strand

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        if not self.exons:
            errors.append(
                ValidationErrorInfo("exons", "At least one exon must be provided")
            )
        for exon in self.exons:
            errors.extend(exon.validate(**kwargs))
        if self.strand not in [-1, 1]:
            errors.append(
                ValidationErrorInfo("strand", "Strand must be either -1 or 1")
            )
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            exons=[Location.from_json(exon, **kwargs) for exon in raw["exons"]],
            strand=raw["strand"],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        return {"exons": [exon.to_json() for exon in self.exons], "strand": self.strand}


class Addition:
    id: NovelGeneId
    location: GeneLocation
    translation: str | None

    VALID_AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

    def __init__(
        self,
        id: NovelGeneId,
        location: GeneLocation,
        translation: str | None,
        validate: bool = True,
        **kwargs,
    ):
        self.id = id
        self.location = location
        self.translation = translation

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        errors.extend(self.id.validate())
        errors.extend(self.location.validate(**kwargs))
        quality: QualityLevel | None = kwargs.get("quality")
        if quality != QualityLevel.QUESTIONABLE and not self.translation:
            errors.append(
                ValidationErrorInfo(
                    "Genes.Addition.translation", "Translation must be provided"
                )
            )
        if self.translation and not all(
            aa in self.VALID_AMINO_ACIDS for aa in self.translation
        ):
            errors.append(
                ValidationErrorInfo(
                    "Genes.Addition.translation", "Invalid amino acid in translation"
                )
            )

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            id=NovelGeneId.from_json(raw["id"]),
            location=GeneLocation.from_json(raw["location"], **kwargs),
            translation=raw.get("translation"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id.to_json(),
            "location": self.location.to_json(),
            "translation": self.translation,
        }


class Deletion:
    id: GeneId
    reason: str

    def __init__(self, id: GeneId, reason: str, validate: bool = True, **kwargs):
        self.id = id
        self.reason = reason

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        errors.extend(self.id.validate(**kwargs))
        if not self.reason:
            errors.append(
                ValidationErrorInfo("Genes.Deletion.reason", "Reason must be provided")
            )
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(id=GeneId.from_json(raw["id"], **kwargs), reason=raw["reason"])

    def to_json(self) -> dict[str, Any]:
        return {"id": self.id.to_json(), "reason": self.reason}


class TailoringFunction:
    function: str
    references: list[Citation]
    db_reference: str | None
    details: str | None

    VALID_FUNCTIONS = (
        "Acetylation",
        "Acylation",
        "Amination",
        "Biaryl bond formation",
        "Carboxylation",
        "Cyclization",
        "Deamination",
        "Decarboxylation",
        "Dehydration",
        "Dehydrogenation",
        "Demethylation",
        "Dioxygenation",
        "Epimerization",
        "FADH2 supply for chlorination",
        "Glycosylation",
        "Halogenation",
        "Heterocyclization",
        "Hydrolysis",
        "Hydroxylation",
        "Lasso macrolactam formation",
        "Methylation",
        "Monooxygenation",
        "Oxidation",
        "Phosphorylation",
        "Prenylation",
        "Reduction",
        "Sulfation",
        "Other",
    )
    REFERENCE_PATTERN = r"^mite:MITE\d{7,7}$"

    def __init__(
        self,
        function: str,
        references: list[Citation],
        db_reference: str | None,
        details: str | None,
        validate: bool = True,
        **kwargs,
    ):
        self.function = function
        self.references = references
        self.db_reference = db_reference
        self.details = details

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        quality: QualityLevel | None = kwargs.get("quality")

        if self.function not in self.VALID_FUNCTIONS:
            errors.append(
                ValidationErrorInfo(
                    "TailoringFunction", f"Invalid tailoring function: {self.function}"
                )
            )

        errors.extend(
            validate_citation_list(self.references, "Tailoring function references", quality=quality)
        )

        if self.db_reference and not re.match(
            self.REFERENCE_PATTERN, self.db_reference
        ):
            errors.append(
                ValidationErrorInfo(
                    "TailoringFunction",
                    f"Invalid database reference {self.db_reference}",
                )
            )
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            function=raw["function"],
            references=[Citation.from_json(ref) for ref in raw["references"]],
            db_reference=raw.get("db_reference"),
            details=raw.get("details"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "function": self.function,
            "references": [ref.to_json() for ref in self.references],
        }
        if self.db_reference:
            ret["db_reference"] = self.db_reference
        if self.details:
            ret["details"] = self.details
        return ret


class Annotation:
    id: GeneId
    name: NovelGeneId | None
    aliases: list[NovelGeneId] | None
    product: str | None
    functions: list[GeneFunction] | None
    tailoring_functions: list[TailoringFunction] | None
    domains: list[Domain] | None
    mutation_phenotype: MutationPhenotype | None
    comment: str | None

    def __init__(
        self,
        id: GeneId,
        name: NovelGeneId | None = None,
        aliases: list[NovelGeneId] | None = None,
        product: str | None = None,
        functions: list[GeneFunction] | None = None,
        tailoring_functions: list[TailoringFunction] | None = None,
        domains: list[Domain] | None = None,
        mutation_phenotype: MutationPhenotype | None = None,
        comment: str | None = None,
        validate: bool = True,
        **kwargs,
    ):
        self.id = id
        self.name = name
        self.aliases = aliases
        self.product = product
        self.functions = functions
        self.tailoring_functions = tailoring_functions
        self.domains = domains
        self.mutation_phenotype = mutation_phenotype
        self.comment = comment

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        errors.extend(self.id.validate(**kwargs))
        if self.name:
            errors.extend(self.name.validate(**kwargs))
        if self.aliases:
            for alias in self.aliases:
                errors.extend(alias.validate(**kwargs))
        if self.functions:
            for function in self.functions:
                errors.extend(function.validate())
        if self.tailoring_functions:
            for function in self.tailoring_functions:
                errors.extend(function.validate())
        if self.domains:
            for domain in self.domains:
                errors.extend(domain.validate(**kwargs))
        if self.mutation_phenotype:
            errors.extend(self.mutation_phenotype.validate(**kwargs))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            id=GeneId.from_json(raw["id"], **kwargs),
            name=NovelGeneId.from_json(raw["name"]) if "name" in raw else None,
            aliases=[NovelGeneId.from_json(alias) for alias in raw.get("aliases", [])],
            product=raw.get("product"),
            functions=[GeneFunction.from_json(f) for f in raw.get("functions", [])],
            tailoring_functions=[
                TailoringFunction.from_json(f, **kwargs) for f in raw.get("tailoring_functions", [])
            ],
            domains=[Domain.from_json(d, **kwargs) for d in raw.get("domains", [])],
            mutation_phenotype=MutationPhenotype.from_json(raw["mutation_phenotype"], **kwargs) if "mutation_phenotype" in raw else None,
            comment=raw.get("comment"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {"id": self.id.to_json()}
        if self.name:
            ret["name"] = self.name.to_json()
        if self.aliases:
            ret["aliases"] = [a.to_json() for a in self.aliases]
        if self.product:
            ret["product"] = self.product
        if self.functions:
            ret["functions"] = [f.to_json() for f in self.functions]
        if self.tailoring_functions:
            ret["tailoring_functions"] = [f.to_json() for f in self.tailoring_functions]
        if self.domains:
            ret["domains"] = [d.to_json() for d in self.domains]
        if self.mutation_phenotype:
            ret["mutation_phenotype"] = self.mutation_phenotype.to_json()
        if self.comment:
            ret["comment"] = self.comment

        return ret

    def __str__(self) -> str:
        return f"{self.id}({self.name})"


class Genes:
    to_add: list[Addition] | None
    to_delete: list[Deletion] | None
    annotations: list[Annotation] | None

    def __init__(
        self,
        to_add: list[Addition] | None = None,
        to_delete: list[Deletion] | None = None,
        annotations: list[Annotation] | None = None,
        validate: bool = True,
        **kwargs,
    ):
        self.to_add = to_add
        self.to_delete = to_delete
        self.annotations = annotations

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        if self.to_add:
            for addition in self.to_add:
                errors.extend(addition.validate(**kwargs))
        if self.to_delete:
            for deletion in self.to_delete:
                errors.extend(deletion.validate(**kwargs))
        if self.annotations:
            for annotation in self.annotations:
                errors.extend(annotation.validate(**kwargs))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            to_add=[Addition.from_json(a, **kwargs) for a in raw.get("to_add", [])],
            to_delete=[
                Deletion.from_json(d, **kwargs) for d in raw.get("to_delete", [])
            ],
            annotations=[
                Annotation.from_json(a, **kwargs) for a in raw.get("annotations", [])
            ],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {}
        if self.to_add:
            ret["to_add"] = [a.to_json() for a in self.to_add]
        if self.to_delete:
            ret["to_delete"] = [d.to_json() for d in self.to_delete]
        if self.annotations:
            ret["annotations"] = [a.to_json() for a in self.annotations]

        return ret
