from typing import Any, Self

from mibig.converters.shared.common import Citation, GeneId, QualityLevel
from mibig.errors import ValidationError, ValidationErrorInfo


class Terpene:
    subclass: str
    prenyltransferases: list[GeneId]
    synthases: list[GeneId]
    precursor: str | None

    VALID_SUBCLASSES = (
        "Diterpene",
        "Hemiterpene",
        "Monoterpene",
        "Sesquiterpene",
        "Triterpene",
    )

    VALID_PRECURSORS = (
        "DMAPP",
        "FPP",
        "GGPP",
        "GPP",
        "IPP",
    )

    def __init__(
        self,
        subclass: str,
        prenyltransferases: list[GeneId],
        synthases: list[GeneId],
        precursor: str | None = None,
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.subclass = subclass
        self.prenyltransferases = prenyltransferases
        self.synthases = synthases
        self.precursor = precursor

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []

        quality: QualityLevel | None = kwargs.get("quality")

        if (
            quality != QualityLevel.QUESTIONABLE
            and self.subclass not in self.VALID_SUBCLASSES
        ):
            errors.append(
                ValidationErrorInfo(
                    "Terpene.subclass", f"Invalid subclass: {self.subclass}"
                )
            )

        for prenyltransferase in self.prenyltransferases:
            errors.extend(prenyltransferase.validate(**kwargs))

        for synthase in self.synthases:
            errors.extend(synthase.validate(**kwargs))

        if self.precursor and self.precursor not in self.VALID_PRECURSORS:
            errors.append(
                ValidationErrorInfo(
                    "Terpene.precursor", f"Invalid precursor: {self.precursor}"
                )
            )

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            subclass=raw["subclass"],
            prenyltransferases=[
                GeneId.from_json(p, **kwargs) for p in raw.get("prenyltransferases", [])
            ],
            synthases=[GeneId.from_json(s, **kwargs) for s in raw.get("synthases", [])],
            precursor=raw.get("precursor"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "subclass": self.subclass,
        }

        if self.prenyltransferases:
            ret["prenyltransferases"] = [p.to_json() for p in self.prenyltransferases]

        if self.synthases:
            ret["synthases"] = [s.to_json() for s in self.synthases]

        if self.precursor:
            ret["precursor"] = self.precursor

        return ret

    @property
    def references(self) -> list[Citation]:
        return []
