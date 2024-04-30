from typing import Any, Self

from mibig.converters.shared.common import Citation, GeneId, QualityLevel
from mibig.converters.shared.mibig.biosynthesis.common import Monomer
from mibig.errors import ValidationError, ValidationErrorInfo


class PKS:
    subclass: str
    cyclases: list[GeneId]
    starter_unit: Monomer | None
    ketide_length: int | None
    iterative: bool | None

    VALID_SUBCLASSES = (
        "Type I",
        "Type II aromatic",
        "Type II highly reducing",
        "Type II arylpolyene",
        "Type III",
    )

    def __init__(
        self,
        subclass: str,
        cyclases: list[GeneId],
        starter_unit: Monomer | None = None,
        ketide_length: int | None = None,
        iterative: bool | None = None,
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.subclass = subclass
        self.cyclases = cyclases
        self.starter_unit = starter_unit
        self.ketide_length = ketide_length
        self.iterative = iterative

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(
        self, quality: QualityLevel | None = None, **kwargs
    ) -> list[ValidationErrorInfo]:
        errors = []

        if (
            quality != QualityLevel.QUESTIONABLE
            and self.subclass not in self.VALID_SUBCLASSES
        ):
            errors.append(
                ValidationErrorInfo(
                    "PKS.subclass", f"Invalid subclass: {self.subclass}"
                )
            )

        for cyclase in self.cyclases:
            errors.extend(cyclase.validate(**kwargs))

        if self.starter_unit:
            errors.extend(self.starter_unit.validate())

        if self.ketide_length and self.ketide_length < 1:
            errors.append(
                ValidationErrorInfo(
                    "PKS.ketide_length", f"Invalid ketide length: {self.ketide_length}"
                )
            )

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            subclass=raw["subclass"],
            cyclases=[GeneId.from_json(c) for c in raw.get("cyclases", [])],
            starter_unit=Monomer.from_json(raw["starter_unit"])
            if "starter_unit" in raw
            else None,
            ketide_length=raw.get("ketide_length"),
            iterative=raw.get("iterative"),
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "subclass": self.subclass,
            "cyclases": [c.to_json() for c in self.cyclases],
        }

        if self.starter_unit:
            ret["starter_unit"] = self.starter_unit.to_json()

        if self.ketide_length:
            ret["ketide_length"] = self.ketide_length

        if self.iterative:
            ret["iterative"] = self.iterative

        return ret

    @property
    def references(self) -> list[Citation]:
        return []
