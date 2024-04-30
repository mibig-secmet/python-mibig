from enum import Enum
from typing import Any, Self

from mibig.converters.shared.mibig.common import QualityLevel
from mibig.errors import ValidationError, ValidationErrorInfo

from .nrps import NRPS
from .other import Other
from .pks import PKS
from .ribosomal import Ribosomal
from .saccharide import Saccharide
from .terpene import Terpene

class SynthesisType(Enum):
    NRPS = "NRPS"
    PKS = "PKS"
    RIBOSOMAL = "ribosomal"
    SACCHARIDE = "saccharide"
    TERPENE = "TERPENE"
    OTHER = "OTHER"

ExtraInfo = NRPS | PKS | Ribosomal | Saccharide | Terpene | Other

MAPPING: dict[SynthesisType, type[ExtraInfo]] = {
    SynthesisType.NRPS: NRPS,
    SynthesisType.PKS: PKS,
    SynthesisType.RIBOSOMAL: Ribosomal,
    SynthesisType.SACCHARIDE: Saccharide,
    SynthesisType.TERPENE: Terpene,
    SynthesisType.OTHER: Other,
}


class BiosynthesisClass:
    class_name: SynthesisType
    extra_info: ExtraInfo

    def __init__(self, class_name: SynthesisType, extra_info: ExtraInfo, validate: bool = True, **kwargs) -> None:
        self.class_name = class_name
        self.extra_info = extra_info

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, quality: QualityLevel | None = None, **kwargs) -> list[ValidationErrorInfo]:
        errors = []

        if quality and quality is not QualityLevel.QUESTIONABLE:
            errors = self.extra_info.validate(**kwargs)

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        class_name = raw["class"]
        extra_info = MAPPING[SynthesisType(class_name)].from_json(raw, **kwargs)

        return cls(
            class_name=SynthesisType(class_name),
            extra_info=extra_info,
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "class": self.class_name.value,
            **self.extra_info.to_json(),
        }
