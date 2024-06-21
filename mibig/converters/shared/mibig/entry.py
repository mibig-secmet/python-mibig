import re
from typing import Any, Self

from mibig.converters.shared.common import ChangeLog, Citation
from mibig.converters.shared.mibig.biosynthesis import Biosynthesis
from mibig.converters.shared.mibig.common import (
    Locus,
    Taxonomy,
    QualityLevel,
    StatusLevel,
    CompletenessLevel,
)
from mibig.converters.shared.mibig.compound import Compound
from mibig.converters.shared.mibig.genes import Genes
from mibig.errors import ValidationError, ValidationErrorInfo


class MibigEntry:
    accession: str
    version: int
    changelog: ChangeLog
    quality: QualityLevel
    status: StatusLevel
    completeness: CompletenessLevel
    loci: list[Locus]
    biosynthesis: Biosynthesis
    compounds: list[Compound]
    taxonomy: Taxonomy
    genes: Genes | None
    retirement_reasons: list[str]
    see_also: list[str]
    comment: str | None
    _legacy_references: list[Citation]

    ENTRY_PATTERN = re.compile(r"^(BGC\d{7,7}|new\d{3,3})$")

    def __init__(
        self,
        accession: str,
        version: int,
        changelog: ChangeLog,
        quality: QualityLevel,
        status: StatusLevel,
        completeness: CompletenessLevel,
        loci: list[Locus],
        biosynthesis: Biosynthesis,
        compounds: list[Compound],
        taxonomy: Taxonomy,
        genes: Genes | None = None,
        retirement_reasons: list[str] | None = None,
        see_also: list[str] | None = None,
        comment: str | None = None,
        _legacy_references: list[Citation] | None = None,
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
        self.biosynthesis = biosynthesis
        self.compounds = compounds
        self.taxonomy = taxonomy
        self.genes = genes
        self.retirement_reasons = retirement_reasons or []
        self.see_also = see_also or []
        self.comment = comment
        self._legacy_references = _legacy_references or []

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        if not self.ENTRY_PATTERN.match(self.accession):
            errors.append(
                ValidationErrorInfo(
                    "MibigEntry.accession", f"Invalid accession: {self.accession}"
                )
            )

        if self.status == StatusLevel.RETIRED and not self.retirement_reasons:
            errors.append(
                ValidationErrorInfo(
                    "MibigEntry.retirement_reasons",
                    "Retirement reasons must be provided for retired entries",
                )
            )

        errors.extend(self.changelog.validate())

        for locus in self.loci:
            errors.extend(locus.validate(quality=self.quality, **kwargs))

        errors.extend(self.biosynthesis.validate(quality=self.quality, **kwargs))

        for compound in self.compounds:
            errors.extend(compound.validate(quality=self.quality, **kwargs))

        errors.extend(self.taxonomy.validate(**kwargs))

        if self.genes:
            errors.extend(self.genes.validate(quality=self.quality, **kwargs))

        if self.quality > QualityLevel.QUESTIONABLE and self._legacy_references:
            errors.append(
                ValidationErrorInfo(
                    "MibigEntry._legacy_references",
                    "Legacy references are only allowed for questionable entries",
                )
            )

        return errors

    def __str__(self) -> str:
        ret = f"MibigEntry({self.accession_version}, {self.quality}, {self.status}, {self.completeness})"

        if self.comment:
            ret += f" - {self.comment}"

        return ret

    @property
    def accession_version(self) -> str:
        return f"{self.accession}.{self.version}"

    @property
    def references(self) -> list[Citation]:
        publications = set()
        for locus in self.loci:
            for evidence in locus.evidence:
                publications.update(evidence.references)

        for compound in self.compounds:
            for evidence in compound.evidence:
                publications.update(evidence.references)

        publications.update(self.biosynthesis.references)

        if self.genes:
            publications.update(self.genes.references)

        publications.update(self._legacy_references)

        return sorted(list(publications))

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        changelog = ChangeLog.from_json(raw["changelog"])
        quality = QualityLevel(raw["quality"])
        status = StatusLevel(raw["status"])
        completeness = CompletenessLevel(raw["completeness"])
        loci = [Locus.from_json(locus, quality=quality) for locus in raw["loci"]]
        compounds = [Compound.from_json(c, quality=quality) for c in raw["compounds"]]
        taxonomy = Taxonomy.from_json(raw["taxonomy"])
        genes = (
            Genes.from_json(raw["genes"], quality=quality, **kwargs)
            if "genes" in raw
            else None
        )
        biosynthesis = Biosynthesis.from_json(
            raw["biosynthesis"], quality=quality, **kwargs
        )
        legacy_references = [
            Citation.from_json(reference) for reference in raw.get("legacy_references", [])
        ]

        return cls(
            raw["accession"],
            raw["version"],
            changelog,
            quality,
            status,
            completeness,
            loci,
            biosynthesis,
            compounds,
            taxonomy,
            genes,
            raw.get("retirement_reasons"),
            raw.get("see_also"),
            raw.get("comment"),
            _legacy_references=legacy_references,
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "accession": self.accession,
            "version": self.version,
            "changelog": self.changelog.to_json(),
            "quality": self.quality.value,
            "status": self.status.value,
            "completeness": self.completeness.value,
            "loci": [locus.to_json() for locus in self.loci],
            "biosynthesis": self.biosynthesis.to_json(),
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

        if self._legacy_references:
            ret["legacy_references"] = [ref.to_json() for ref in self._legacy_references]

        return ret
