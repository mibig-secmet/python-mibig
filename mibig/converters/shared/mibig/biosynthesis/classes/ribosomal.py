from typing import Any, Self

from mibig.converters.shared.common import Citation, GeneId, Location, QualityLevel
from mibig.errors import ValidationError, ValidationErrorInfo
from mibig.utils import CDS, Record


class Crosslink:
    begin: int
    end: int
    link_type: str | None
    details: str | None

    def __init__(
        self,
        begin: int,
        end: int,
        link_type: str | None,
        details: str | None = None,
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.begin = begin
        self.end = end
        self.link_type = link_type
        self.details = details

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, cds: CDS | None = None) -> list[ValidationErrorInfo]:
        errors = []

        if self.begin < 0:
            errors.append(
                ValidationErrorInfo(
                    "RippCrosslink.from", "From must be greater than or equal to 0"
                )
            )
        if self.end < 0:
            errors.append(
                ValidationErrorInfo(
                    "RippCrosslink.to", "To must be greater than or equal to 0"
                )
            )
        if self.begin >= self.end:
            errors.append(
                ValidationErrorInfo("RippCrosslink.from", "From must be less than to")
            )

        if cds:
            if self.begin >= cds.translation_length:
                errors.append(
                    ValidationErrorInfo(
                        "RippCrosslink.from",
                        "From must be less than the length of the CDS",
                    )
                )
            if self.end > cds.translation_length:
                errors.append(
                    ValidationErrorInfo(
                        "RippCrosslink.to",
                        "To must be less than or equal to the length of the CDS",
                    )
                )

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            begin=raw["from"],
            end=raw["to"],
            link_type=raw.get("type"),
            details=raw.get("details"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "from": self.begin,
            "to": self.end,
        }
        if self.link_type:
            ret["type"] = self.link_type
        if self.details:
            ret["details"] = self.details

        return ret


class Precursor:
    gene: GeneId
    core_sequence: str
    leader_cleavage_location: Location | None
    follower_clavage_location: Location | None
    crosslinks: list[Crosslink]
    recognition_motif: str | None

    def __init__(
        self,
        gene: GeneId,
        core_sequence: str,
        leader_cleavage_location: Location | None,
        follower_clavage_location: Location | None,
        crosslinks: list[Crosslink],
        recognition_motif: str | None = None,
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.gene = gene
        self.core_sequence = core_sequence
        self.leader_cleavage_location = leader_cleavage_location
        self.follower_clavage_location = follower_clavage_location
        self.crosslinks = crosslinks
        self.recognition_motif = recognition_motif

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []

        cds: CDS | None = None
        errors.extend(self.gene.validate(**kwargs))
        if kwargs.get("record"):
            record: Record = kwargs["record"]
            cds = record.get_cds(str(self.gene))

        if self.leader_cleavage_location:
            errors.extend(self.leader_cleavage_location.validate(**kwargs))
        if self.follower_clavage_location:
            errors.extend(self.follower_clavage_location.validate(**kwargs))
        for crosslink in self.crosslinks:
            errors.extend(crosslink.validate(cds))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        gene = GeneId.from_json(raw["gene"], **kwargs)
        cds: CDS | None = None
        if kwargs.get("record"):
            record: Record = kwargs["record"]
            cds = record.get_cds(str(gene))
        leader_cleavage_location = None
        follower_clavage_location = None
        if "leader_cleavage_location" in raw:
            leader_cleavage_location = Location.from_json(
                raw["leader_cleavage_location"], **kwargs
            )
        if "follower_clavage_location" in raw:
            follower_clavage_location = Location.from_json(
                raw["follower_clavage_location"], **kwargs
            )
        return cls(
            gene=gene,
            core_sequence=raw["core_sequence"],
            leader_cleavage_location=leader_cleavage_location,
            follower_clavage_location=follower_clavage_location,
            crosslinks=[
                Crosslink.from_json(crosslink, cds=cds)
                for crosslink in raw.get("crosslinks", [])
            ],
            recognition_motif=raw.get("recognition_motif"),
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "gene": self.gene.to_json(),
            "core_sequence": self.core_sequence,
        }
        if self.crosslinks:
            ret["crosslinks"] = [crosslink.to_json() for crosslink in self.crosslinks]
        if self.leader_cleavage_location:
            ret["leader_cleavage_location"] = self.leader_cleavage_location.to_json()
        if self.follower_clavage_location:
            ret["follower_clavage_location"] = self.follower_clavage_location.to_json()
        if self.recognition_motif:
            ret["recognition_motif"] = self.recognition_motif

        return ret


class Ribosomal:
    subclass: str
    precursors: list[Precursor]
    ripp_type: str | None
    details: str | None
    peptidases: list[GeneId]

    VALID_SUBCLASSES = (
        "RiPP",
        "unmodified",
    )

    VALID_RIPP_TYPES = (
        "Atropopeptide",
        "Biarylitide",
        "Bottromycin",
        "Borosin",
        "Crocagin",
        "Cyanobactin",
        "Cyptide",
        "Dikaritin",
        "Epipeptide",
        "Glycocin",
        "Guanidinotide",
        "Head-to-tail cyclized peptide",
        "Lanthipeptide",
        "LAP",
        "Lasso peptide",
        "Linaridin",
        "Methanobactin",
        "Microcin",
        "Microviridin",
        "Mycofactocin",
        "Pearlin",
        "Proteusin",
        "Ranthipeptide",
        "Rotapeptide",
        "Ryptide",
        "Sactipeptide",
        "Spliceotide",
        "Streptide",
        "Sulfatyrotide",
        "Thioamidide",
        "Thiopeptide",
        "other",
    )

    def __init__(
        self,
        subclass: str,
        precursors: list[Precursor],
        ripp_type: str | None = None,
        details: str | None = None,
        peptidases: list[GeneId] | None = None,
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.subclass = subclass
        self.precursors = precursors
        self.ripp_type = ripp_type
        self.details = details
        self.peptidases = peptidases or []

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []

        quality: QualityLevel | None = kwargs.get("quality")

        if self.subclass not in self.VALID_SUBCLASSES:
            errors.append(
                ValidationErrorInfo(
                    "Ribosomal.subclass",
                    f"Subclass must be one of {', '.join(self.VALID_SUBCLASSES)}",
                )
            )

        if self.subclass == "RiPP":
            if (
                quality != QualityLevel.QUESTIONABLE
                and self.ripp_type not in self.VALID_RIPP_TYPES
            ):
                errors.append(
                    ValidationErrorInfo(
                        "Ribosomal.ripp_type", f"Invalid RiPP type: {self.ripp_type}"
                    )
                )
            if self.ripp_type == "other" and not self.details:
                errors.append(
                    ValidationErrorInfo(
                        "Ribosomal.details",
                        "Details must be provided for 'other' RiPP types",
                    )
                )

        for precursor in self.precursors:
            errors.extend(precursor.validate(**kwargs))

        for peptidase in self.peptidases:
            errors.extend(peptidase.validate(**kwargs))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            subclass=raw["subclass"],
            precursors=[
                Precursor.from_json(precursor, **kwargs)
                for precursor in raw["precursors"]
            ],
            ripp_type=raw.get("ripp_type"),
            details=raw.get("details"),
            peptidases=[
                GeneId.from_json(peptidase, **kwargs)
                for peptidase in raw.get("peptidases", [])
            ],
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "subclass": self.subclass,
            "precursors": [precursor.to_json() for precursor in self.precursors],
        }
        if self.ripp_type:
            ret["ripp_type"] = self.ripp_type
        if self.details:
            ret["details"] = self.details
        if self.peptidases:
            ret["peptidases"] = [peptidase.to_json() for peptidase in self.peptidases]

        return ret

    @property
    def references(self) -> list[Citation]:
        return []
