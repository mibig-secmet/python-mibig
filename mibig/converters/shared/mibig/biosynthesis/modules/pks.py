from typing import Any, Self

from mibig.converters.shared.mibig.biosynthesis.domains.base import Domain
from mibig.errors import ValidationErrorInfo

from .core import ModuleInfo


class PksTransAtStarter(ModuleInfo):
    pass


class PksTransAt(ModuleInfo):
    ks_domain: Domain

    def __init__(
        self,
        ks_domain: Domain,
        carriers: list[Domain],
        modification_domains: list[Domain],
        **kwargs,
    ) -> None:
        self.ks_domain = ks_domain
        super().__init__(carriers, modification_domains, core_domains=[ks_domain], **kwargs)

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        new = cls(
            ks_domain=Domain.from_json(raw.pop("ks_domain"), **kwargs),
            carriers=[Domain.from_json(carrier, **kwargs) for carrier in raw.pop("carriers")],
            modification_domains=[
                Domain.from_json(domain, **kwargs)
                for domain in raw.pop("modification_domains", [])
            ],
            **kwargs,
        )
        assert not raw
        return new

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret.pop("core_domains")
        ret.update({
            "ks_domain": self.ks_domain.to_json(),
        })
        return ret


class PksModularStarter:
    at_domain: Domain

    def __init__(
        self,
        at_domain: Domain,
        carriers: list[Domain],
        modification_domains: list[Domain],
        core_domains: list[Domain] = None,
        **kwargs,
    ) -> None:
        self.at_domain = at_domain
        super().__init__(carriers, modification_domains, core_domains=[at_domain] + (core_domains or []), **kwargs)

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        new = cls(
            at_domain=Domain.from_json(raw.pop("at_domain"), **kwargs),
            carriers=[Domain.from_json(carrier, **kwargs) for carrier in raw.pop("carriers")],
            modification_domains=[
                Domain.from_json(domain, **kwargs)
                for domain in raw.pop("modification_domains", [])
            ],
            **kwargs,
        )
        assert not raw
        return new

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret.pop("core_domains")
        ret.update({
            "at_domain": self.at_domain.to_json(),
        })
        return ret


class PksModular(PksModularStarter):
    ks_domain: Domain

    def __init__(
        self,
        at_domain: Domain,
        ks_domain: Domain,
        carriers: list[Domain],
        modification_domains: list[Domain],
        **kwargs,
    ) -> None:
        self.ks_domain = ks_domain
        super().__init__(at_domain, carriers, modification_domains, core_domains=[ks_domain, at_domain], **kwargs)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = super().validate(**kwargs)
        errors.extend(self.at_domain.validate(**kwargs))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        new = cls(
            at_domain=Domain.from_json(raw.pop("at_domain"), **kwargs),
            ks_domain=Domain.from_json(raw.pop("ks_domain"), **kwargs),
            carriers=[Domain.from_json(carrier, **kwargs) for carrier in raw.pop("carriers")],
            modification_domains=[
                Domain.from_json(domain, **kwargs)
                for domain in raw.pop("modification_domains", [])
            ],
            **kwargs,
        )
#        assert not raw
        return new

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
        **kwargs,
    ) -> None:
        self.iterations = iterations
        super().__init__(
            at_domain, ks_domain, carriers, modification_domains, **kwargs,
        )

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = super().validate(**kwargs)
        if self.iterations < 1:
            errors.append(ValidationErrorInfo("iterations", "Must be greater than 0"))
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        new = cls(
            at_domain=Domain.from_json(raw.pop("at_domain")),
            ks_domain=Domain.from_json(raw.pop("ks_domain")),
            carriers=[Domain.from_json(carrier) for carrier in raw.pop("carriers")],
            modification_domains=[
                Domain.from_json(domain)
                for domain in raw.pop("modification_domains", [])
            ],
            iterations=raw["iterations"],
            **kwargs,
        )
        return new

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret["iterations"] = self.iterations
        return ret
