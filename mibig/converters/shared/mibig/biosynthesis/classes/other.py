from typing import Any, Self

from mibig.converters.shared.common import Citation, QualityLevel
from mibig.errors import ValidationError, ValidationErrorInfo


class Other:
    subclass: str
    details: str | None

    VALID_SUBCLASSES = (
        "aminocoumarin",
        "butyrolactone",
        "cyclitol",
        "ectoine",
        "fatty acid",
        "flavin",
        "indole",
        "non-nrp beta-lactam",
        "non-nrp siderophore",
        "nucleoside",
        "other",
        "pbde",
        "phenazine",
        "phosphonate",
        "shikimate-derived",
        "trna-derived",
    )

    def __init__(
        self, subclass: str, details: str | None = None, validate: bool = True, **kwargs
    ) -> None:
        self.subclass = subclass
        self.details = details

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(
        self, quality: QualityLevel | None = None, **kwargs
    ) -> list[ValidationErrorInfo]:
        errors = []

        if self.subclass not in self.VALID_SUBCLASSES:
            errors.append(
                ValidationErrorInfo(
                    "Other.subclass", f"Invalid subclass: {self.subclass}"
                )
            )

        if self.subclass == "other" and not self.details:
            errors.append(
                ValidationErrorInfo(
                    "Other.details", "Missing details for subclass 'other'"
                )
            )

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            subclass=raw["subclass"],
            details=raw.get("details"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "subclass": self.subclass,
        }
        if self.details:
            ret["details"] = self.details

        return ret

    @property
    def references(self) -> list[Citation]:
        return []
