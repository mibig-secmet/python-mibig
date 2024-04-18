from typing import Any, Self

from mibig.converters.shared.mibig.biosynthesis.domains.base import Domain
from mibig.errors import ValidationError, ValidationErrorInfo

class CAL:
    modification_domains: list[Domain]

    def __init__(self, modification_domains: list[Domain], validate: bool = True, **kwargs) -> None:
        self.modification_domains = modification_domains

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        for domain in self.modification_domains:
            errors.extend(domain.validate(**kwargs))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            modification_domains=[Domain.from_json(domain, **kwargs) for domain in raw.get("modification_domains", [])],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {}

        if self.modification_domains:
            ret["modification_domains"] = [domain.to_json() for domain in self.modification_domains]

        return ret

