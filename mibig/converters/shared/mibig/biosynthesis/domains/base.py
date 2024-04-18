from enum import Enum
from typing import Any, Self, Union

from mibig.converters.shared.common import GeneId, Location
from mibig.errors import ValidationError, ValidationErrorInfo

from .acyltransferase import Acyltransferase
from .adenylation import Adenylation
from .aminotransferase import Aminotransferase
from .carrier import Carrier
from .condensation import Condensation
from .cyclase import Cyclase
from .dehydratase import Dehydratase
from .enoylreductase import Enoylreductase
from .epimerase import Epimerase
from .hydroxylase import Hydroxylase
from .ketoreductase import Ketoreductase
from .ligase import Ligase
from .methyltransferase import Methyltransferase
from .other import Other
from .oxidase import Oxidase
from .thioesterase import Thioesterase
from .thioreductase import Thioreductase


class DomainType(Enum):
    ACYLTRANSFERASE = "acyltransferase"
    ADENYLATION = "adenylation"
    AMINOTRANSFERASE = "aminotransferase"
    CARRIER = "carrier"
    CONDENSATION = "condensation"
    CYCLASE = "cyclase"
    DEHYDRATASE = "dehydratase"
    ENOYLREDUCTASE = "enoylreductase"
    EPIMERASE = "epimerase"
    HYDROXYLASE = "hydroxylase"
    KETOREDUCTASE = "ketoreductase"
    LIGASE = "ligase"
    METHYLTRANSFERASE = "methyltransferase"
    OTHER = "other"
    OXIDASE = "oxidase"
    THIOESTERASE = "thioesterase"
    THIOREDUCTASE = "thioreductase"


ExtraInfo = Union[
    Acyltransferase,
    Aminotransferase,
    Adenylation,
    Carrier,
    Condensation,
    Cyclase,
    Dehydratase,
    Enoylreductase,
    Epimerase,
    Hydroxylase,
    Ketoreductase,
    Ligase,
    Methyltransferase,
    Other,
    Oxidase,
    Thioesterase,
    Thioreductase,]

MAPPING: dict[DomainType, type[ExtraInfo]] = {
    DomainType.ACYLTRANSFERASE: Acyltransferase,
    DomainType.ADENYLATION: Adenylation,
    DomainType.AMINOTRANSFERASE: Aminotransferase,
    DomainType.CARRIER: Carrier,
    DomainType.CONDENSATION: Condensation,
    DomainType.CYCLASE: Cyclase,
    DomainType.DEHYDRATASE: Dehydratase,
    DomainType.ENOYLREDUCTASE: Enoylreductase,
    DomainType.EPIMERASE: Epimerase,
    DomainType.HYDROXYLASE: Hydroxylase,
    DomainType.KETOREDUCTASE: Ketoreductase,
    DomainType.LIGASE: Ligase,
    DomainType.METHYLTRANSFERASE: Methyltransferase,
    DomainType.OTHER: Other,
    DomainType.OXIDASE: Oxidase,
    DomainType.THIOESTERASE: Thioesterase,
    DomainType.THIOREDUCTASE: Thioreductase,
}


class Domain:
    domain_type: DomainType
    gene: GeneId
    location: Location
    extra_info: ExtraInfo


    def __init__(self, domain_type: DomainType, gene: GeneId, location: Location, extra_info: ExtraInfo,
                 validate: bool = True, **kwargs) -> None:
        self.domain_type = domain_type
        self.gene = gene
        self.location = location
        self.extra_info = extra_info

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []

        # TODO: Add valication for domain_type
        # errors.extend(self.domain_type.value.validate(**kwargs))

        errors.extend(self.gene.validate(record=kwargs.get("record")))
        cds = None
        if "record" in kwargs:
            cds = kwargs["record"].get_cds(str(self.gene))
        errors.extend(self.location.validate(cds=cds))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        domain_type = DomainType(raw["type"])

        extra_info = MAPPING[domain_type].from_json(raw, **kwargs)

        return cls(
            domain_type=domain_type,
            gene=GeneId.from_json(raw["gene"], **kwargs),
            location=Location.from_json(raw["location"], **kwargs),
            extra_info=extra_info,
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "type": self.domain_type.value,
            "gene": self.gene.to_json(),
            "location": self.location.to_json(),
            **self.extra_info.to_json(),
        }
