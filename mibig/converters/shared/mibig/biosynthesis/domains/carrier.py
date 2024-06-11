from typing import Any, Self

from mibig.errors import ValidationError, ValidationErrorInfo


class Carrier:
    subtype: str | None
    beta_branching: bool | None

    VALID_SUBTYPES = (
        "ACP",
        "PCP",
    )

    def __init__(self, subtype: str | None = None, beta_branching: bool | None = None, validate: bool = True, **kwargs) -> None:
        self.subtype = subtype
        self.beta_branching = beta_branching

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **_) -> list[ValidationErrorInfo]:
        errors = []

        if self.subtype and self.subtype not in self.VALID_SUBTYPES:
            errors.append(ValidationErrorInfo("Carrier.subtype", f"Invalid subtype: {self.subtype}"))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            subtype=raw.get("subtype"),
            beta_branching=raw.get("beta_branching"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {}
        if self.subtype:
            ret["subtype"] = self.subtype

        if self.beta_branching is not None:
            ret["beta_branching"] = self.beta_branching

        return ret
