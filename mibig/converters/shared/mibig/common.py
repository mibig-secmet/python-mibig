from enum import Enum
from typing import Any, Self

from mibig.converters.shared.common import Location, Evidence, QualityLevel as QualityLevel
from mibig.errors import ValidationError
from mibig.utils import Record
from mibig.validation import ValidationErrorInfo


class CompletenessLevel(Enum):
    UNKNOWN = "unknown"
    PARTIAL = "partial"
    COMPLETE = "complete"


class SubstrateEvidence(Evidence):
    VALID_METHODS = {
        "Activity assay",
        "ACVS assay",
        "ATP-PPi exchange assay",
        "Enzyme-coupled assay",
        "Feeding study",
        "Heterologous expression",
        "Homology",
        "HPLC",
        "In-vitro experiments",
        "Knock-out studies",
        "Mass spectrometry",
        "NMR",
        "Radio labelling",
        "Sequence-based prediction",
        "Steady-state kinetics",
        "Structure-based inference",
        "X-ray crystallography",
    }


class LocusEvidence(Evidence):
    VALID_METHODS = {
        "Homology-based prediction",
        "Correlation of genomic and metabolomic data",
        "Gene expression correlated with compound production",
        "Knock-out studies",
        "Enzymatic assays",
        "Heterologous expression",
        "In vitro expression",
    }


class Locus:
    accession: str
    location: Location
    evidence: list[LocusEvidence]

    def __init__(self, accession: str, location: Location, evidence: list[LocusEvidence],
                 validate: bool = True, **kwargs) -> None:
        self.accession = accession
        self.location = location
        self.evidence = evidence

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if "record" in kwargs:
            record: Record = kwargs["record"]
            if record.id != self.accession:
                errors.append(ValidationErrorInfo("Locus.accession", f"Accession mismatch: {self.accession} != {record.id}"))
        else:
            if self.accession.count(".") > 1 and not self.accession.startswith("MIBIG."):
                errors.append(ValidationErrorInfo("Locus.accession", f"Invalid accession {self.accession}"))

        errors.extend(self.location.validate(**kwargs))

        for evidence in self.evidence:
            errors.extend(evidence.validate())

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        evidence: list[LocusEvidence] = [LocusEvidence.from_json(e) for e in raw["evidence"]]
        return cls(raw["accession"], Location.from_json(raw["location"], **kwargs), evidence)

    def to_json(self) -> dict[str, Any]:
        return {
            "accession": self.accession,
            "location": self.location.to_json(),
            "evidence": [e.to_json() for e in self.evidence]
        }


class Taxonomy:
    name: str
    ncbi_tax_id: int

    def __init__(self, name: str, ncbi_tax_id: int, validate: bool = True, **kwargs) -> None:
        self.name = name
        self.ncbi_tax_id = ncbi_tax_id

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if "record" in kwargs:
            record: Record = kwargs["record"]
            if record.organism != self.name:
                errors.append(ValidationErrorInfo("Taxonomy.name", f"Name mismatch: {self.name} != {record.organism}"))
            if record.ncbi_tax_id != self.ncbi_tax_id:
                errors.append(ValidationErrorInfo("Taxonomy.ncbi_tax_id", f"NCBI Tax ID mismatch: {self.ncbi_tax_id} != {record.ncbi_tax_id}"))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(raw["name"], raw["ncbiTaxId"], **kwargs)

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "ncbiTaxId": self.ncbi_tax_id,
        }
