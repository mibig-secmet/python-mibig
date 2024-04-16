import re
from typing import Any, Self

from mibig.converters.shared.common import ChangeLog
from mibig.converters.shared.mibig import Locus, Taxonomy
from mibig.converters.shared.mibig.compound import Compound
from mibig.converters.shared.mibig.genes import Genes
from mibig.errors import ValidationError, ValidationErrorInfo


class MibigEntry:
    accession: str
    version: int
    changelog: ChangeLog
    quality: str
    status: str
    completeness: str
    loci: list[Locus]
    # TODO: deal with biosynthesis
    # biosynthesis: Biosynthesis
    compounds: list[Compound]
    taxonomy: Taxonomy
    genes: Genes | None
    retirement_reasons: list[str]
    see_also: list[str]
    comment: str | None

    ENTRY_PATTERN = re.compile(r"^BGC\d{7,7}$")
    COMPLETENESS_LEVELS = ("unknown", "partial", "complete")
    QUALITY_LEVELS = ("questionable", "low", "medium", "high")
    STATUS_LEVELS = ("pending", "embargoed", "active", "retired")

    def __init__(self,
                 accession: str,
                 version: int,
                 changelog: ChangeLog,
                 quality: str,
                 status: str,
                 completeness: str,
                 loci: list[Locus],
                 # biosynthesis: Biosynthesis,
                 compounds: list[Compound],
                 taxonomy: Taxonomy,
                 genes: Genes | None = None,
                 retirement_reasons: list[str] | None = None,
                 see_also: list[str] | None = None,
                 comment: str | None = None,
                 validate: bool = True,
                 **kwargs,
                 ) -> None:
        self.accession = accession
        self.version = version
        self.changelog = changelog
        self.quality = quality
        self.status = status
        self.completeness = completeness
        self.loci = loci
        # self.biosynthesis = biosynthesis
        self.compounds = compounds
        self.taxonomy = taxonomy
        self.genes = genes
        self.retirement_reasons = retirement_reasons or []
        self.see_also = see_also or []
        self.comment = comment

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        if not self.ENTRY_PATTERN.match(self.accession):
            errors.append(ValidationErrorInfo("MibigEntry.accession", f"Invalid accession: {self.accession}"))

        if self.quality not in self.QUALITY_LEVELS:
            errors.append(ValidationErrorInfo("MibigEntry.quality", f"Invalid quality: {self.quality}"))

        if self.status not in self.STATUS_LEVELS:
            errors.append(ValidationErrorInfo("MibigEntry.status", f"Invalid status: {self.status}"))

        if self.status == "retired" and not self.retirement_reasons:
            errors.append(ValidationErrorInfo("MibigEntry.retirement_reasons", "Retirement reasons must be provided for retired entries"))

        if self.completeness not in self.COMPLETENESS_LEVELS:
            errors.append(ValidationErrorInfo("MibigEntry.completeness", f"Invalid completeness: {self.completeness}"))

        errors.extend(self.changelog.validate())

        for locus in self.loci:
            errors.extend(locus.validate(**kwargs))

        for compound in self.compounds:
            errors.extend(compound.validate())

        errors.extend(self.taxonomy.validate(**kwargs))

        if self.genes:
            errors.extend(self.genes.validate(**kwargs))

        return errors


    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        changelog = ChangeLog.from_json(raw["changelog"])
        loci = [Locus.from_json(locus) for locus in raw["loci"]]
        compounds = [Compound.from_json(c) for c in raw["compounds"]]
        taxonomy = Taxonomy.from_json(raw["taxonomy"])
        genes = Genes.from_json(raw["genes"], **kwargs) if "genes" in raw else None

        return cls(
            raw["accession"],
            raw["version"],
            changelog,
            raw["quality"],
            raw["status"],
            raw["completeness"],
            loci,
            compounds,
            taxonomy,
            genes,
            raw.get("retirement_reasons"),
            raw.get("see_also"),
            raw.get("comment"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "accession": self.accession,
            "version": self.version,
            "changelog": self.changelog.to_json(),
            "quality": self.quality,
            "status": self.status,
            "completeness": self.completeness,
            "loci": [locus.to_json() for locus in self.loci],
            "compounds": [c.to_json() for c in self.compounds],
            "taxonomy": self.taxonomy.to_json(),
        }

        if self.genes:
            ret["genes"] = self.genes.to_json()

        if self.retirement_reasons:
            ret["retirement_reasons"] = self.retirement_reasons

        if self.see_also:
            ret["see_also"] = self.see_also

        if self.comment:
            ret["comment"] = self.comment

        return ret
