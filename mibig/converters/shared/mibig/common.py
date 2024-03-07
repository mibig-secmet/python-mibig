from typing import Any, Self


from mibig.errors import ValidationError
from mibig.converters.shared.common import Citation
from mibig.validation import ValidationErrorInfo


class SubstrateEvidence:
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
    method: str
    references: list[Citation]

    def __init__(
        self, method: str, references: list[Citation], validate: bool = True
    ) -> None:
        self.method = method
        self.references = references

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if self.method not in self.VALID_METHODS:
            errors.append(
                ValidationErrorInfo(
                    "SubstrateEvidence.method", f"Invalid method {self.method!r}"
                )
            )

        for ref in self.references:
            errors.extend(ref.validate())

        return errors

    def to_json(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "references": [r.to_json() for r in self.references],
        }

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        method = raw["method"]
        references = [Citation.from_json(r) for r in raw["references"]]
        return cls(method, references)
