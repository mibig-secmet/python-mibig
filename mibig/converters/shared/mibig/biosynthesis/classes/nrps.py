from typing import Any, Self

from mibig.converters.shared.mibig.biosynthesis.common import ReleaseType
from mibig.converters.shared.mibig.biosynthesis.domains.base import Domain
from mibig.converters.shared.mibig.common import QualityLevel
from mibig.errors import ValidationError, ValidationErrorInfo

class NRPS:
    subclass: str
    release_types: list[ReleaseType]
    thioesterases: list[Domain]

    VALID_SUBCLASSES = (
        "Type I",
        "Type II",
        "Type III",
        "Type IV",
        "Type V",
        "Type VI",
    )

    def __init__(self, subclass: str, release_types: list[ReleaseType], thioesterases: list[Domain], validate: bool = True, **kwargs) -> None:
        self.subclass = subclass
        self.release_types = release_types
        self.thioesterases = thioesterases

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, quality: QualityLevel | None = None, **kwargs) -> list[ValidationErrorInfo]:
        errors = []

        if quality and quality is QualityLevel.QUESTIONABLE:
            return errors

        if self.subclass not in self.VALID_SUBCLASSES:
            errors.append(ValidationErrorInfo("NRPS.subclass", f"Invalid subclass: {self.subclass}"))

        for release_type in self.release_types:
            errors.extend(release_type.validate())

        for thioesterase in self.thioesterases:
            errors.extend(thioesterase.validate(**kwargs))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            subclass=raw["subclass"],
            release_types=[ReleaseType.from_json(release_type) for release_type in raw.get("release_types", [])],
            thioesterases=[Domain.from_json(thioesterase, **kwargs) for thioesterase in raw.get("thioesterases", [])],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "subclass": self.subclass,
        }

        if self.release_types:
            ret["release_types"] = [release_type.to_json() for release_type in self.release_types]

        if self.thioesterases:
            ret["thioesterases"] = [thioesterase.to_json() for thioesterase in self.thioesterases]

        return ret
