from typing import Any, Self

from mibig.converters.shared.mibig.biosynthesis.domains.base import Domain
from mibig.errors import ValidationError, ValidationErrorInfo


class PksTransAtStarter:
    carriers: list[Domain]
    modification_domains: list[Domain]

    def __init__(
        self,
        carriers: list[Domain],
        modification_domains: list[Domain],
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.carriers = carriers
        self.modification_domains = modification_domains

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        for carrier in self.carriers:
            errors.extend(carrier.validate(**kwargs))
        for domain in self.modification_domains:
            errors.extend(domain.validate(**kwargs))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            carriers=[Domain.from_json(carrier, **kwargs) for carrier in raw["carriers"]],
            modification_domains=[
                Domain.from_json(domain, **kwargs)
                for domain in raw.get("modification_domains", [])
            ],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "carriers": [carrier.to_json() for carrier in self.carriers],
        }

        if self.modification_domains:
            ret["modification_domains"] = [
                domain.to_json() for domain in self.modification_domains
            ]

        return ret


class PksTransAt:
    ks_domain: Domain
    carriers: list[Domain]
    modification_domains: list[Domain]

    def __init__(
        self,
        ks_domain: Domain,
        carriers: list[Domain],
        modification_domains: list[Domain],
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.ks_domain = ks_domain
        self.carriers = carriers
        self.modification_domains = modification_domains

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        errors.extend(self.ks_domain.validate(**kwargs))
        for carrier in self.carriers:
            errors.extend(carrier.validate(**kwargs))
        for domain in self.modification_domains:
            errors.extend(domain.validate(**kwargs))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            ks_domain=Domain.from_json(raw["ks_domain"], **kwargs),
            carriers=[Domain.from_json(carrier, **kwargs) for carrier in raw["carriers"]],
            modification_domains=[
                Domain.from_json(domain, **kwargs)
                for domain in raw.get("modification_domains", [])
            ],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "ks_domain": self.ks_domain.to_json(),
            "carriers": [carrier.to_json() for carrier in self.carriers],
        }

        if self.modification_domains:
            ret["modification_domains"] = [
                domain.to_json() for domain in self.modification_domains
            ]

        return ret


class PksModularStarter:
    at_domain: Domain
    carriers: list[Domain]
    modification_domains: list[Domain]

    def __init__(
        self,
        at_domain: Domain,
        carriers: list[Domain],
        modification_domains: list[Domain],
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.at_domain = at_domain
        self.carriers = carriers
        self.modification_domains = modification_domains

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        errors.extend(self.at_domain.validate(**kwargs))
        for carrier in self.carriers:
            errors.extend(carrier.validate(**kwargs))
        for domain in self.modification_domains:
            errors.extend(domain.validate(**kwargs))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            at_domain=Domain.from_json(raw["at_domain"], **kwargs),
            carriers=[Domain.from_json(carrier, **kwargs) for carrier in raw["carriers"]],
            modification_domains=[
                Domain.from_json(domain, **kwargs)
                for domain in raw.get("modification_domains", [])
            ],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "at_domain": self.at_domain.to_json(),
            "carriers": [carrier.to_json() for carrier in self.carriers],
        }

        if self.modification_domains:
            ret["modification_domains"] = [
                domain.to_json() for domain in self.modification_domains
            ]

        return ret


class PksModular(PksTransAt):
    at_domain: Domain

    def __init__(
        self,
        at_domain: Domain,
        ks_domain: Domain,
        carriers: list[Domain],
        modification_domains: list[Domain],
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.at_domain = at_domain
        super().__init__(ks_domain, carriers, modification_domains, validate, **kwargs)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = super().validate(**kwargs)
        errors.extend(self.at_domain.validate(**kwargs))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            at_domain=Domain.from_json(raw["at_domain"], **kwargs),
            ks_domain=Domain.from_json(raw["ks_domain"], **kwargs),
            carriers=[Domain.from_json(carrier, **kwargs) for carrier in raw["carriers"]],
            modification_domains=[
                Domain.from_json(domain, **kwargs)
                for domain in raw.get("modification_domains", [])
            ],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret["at_domain"] = self.at_domain.to_json()
        return ret


class PksIterative(PksModular):
    iterations: int

    def __init__(
        self,
        at_domain: Domain,
        ks_domain: Domain,
        carriers: list[Domain],
        modification_domains: list[Domain],
        iterations: int,
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.iterations = iterations
        super().__init__(
            at_domain, ks_domain, carriers, modification_domains, validate, **kwargs
        )

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = super().validate(**kwargs)
        if self.iterations < 1:
            errors.append(ValidationErrorInfo("iterations", "Must be greater than 0"))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            at_domain=Domain.from_json(raw["at_domain"]),
            ks_domain=Domain.from_json(raw["ks_domain"]),
            carriers=[Domain.from_json(carrier) for carrier in raw["carriers"]],
            modification_domains=[
                Domain.from_json(domain)
                for domain in raw.get("modification_domains", [])
            ],
            iterations=raw["iterations"],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret["iterations"] = self.iterations
        return ret
