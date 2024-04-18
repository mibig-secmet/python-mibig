from typing import Any, Self

from mibig.converters.shared.mibig.biosynthesis.domains.base import Domain
from mibig.errors import ValidationError, ValidationErrorInfo


class NrpsTypeI:
    a_domain: Domain
    carriers: list[Domain]
    c_domain: Domain | None
    modification_domains: list[Domain]

    def __init__(self,
                 a_domain: Domain,
                 carriers: list[Domain],
                 c_domain: Domain | None,
                 modification_domains: list[Domain],
                 validate: bool = True, **kwargs) -> None:
        self.a_domain = a_domain
        self.carriers = carriers
        self.c_domain = c_domain
        self.modification_domains = modification_domains

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        errors.extend(self.a_domain.validate(**kwargs))
        for carrier in self.carriers:
            errors.extend(carrier.validate(**kwargs))
        if self.c_domain:
            errors.extend(self.c_domain.validate(**kwargs))
        for domain in self.modification_domains:
            errors.extend(domain.validate(**kwargs))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            a_domain=Domain.from_json(raw["a_domain"]),
            carriers=[Domain.from_json(carrier) for carrier in raw["carriers"]],
            c_domain=Domain.from_json(raw["c_domain"]) if "c_domain" in raw else None,
            modification_domains=[Domain.from_json(domain) for domain in raw.get("modification_domains", [])],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "a_domain": self.a_domain.to_json(),
            "carriers": [carrier.to_json() for carrier in self.carriers],
        }

        if self.c_domain:
            ret["c_domain"] = self.c_domain.to_json()

        if self.modification_domains:
            ret["modification_domains"] = [domain.to_json() for domain in self.modification_domains]

        return ret

