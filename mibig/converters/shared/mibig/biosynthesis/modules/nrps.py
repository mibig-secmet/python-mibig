from typing import Any, Self

from mibig.converters.shared.mibig.biosynthesis.domains.base import Domain

from .core import ModuleInfo


class NrpsTypeI(ModuleInfo):
    a_domain: Domain
    c_domain: Domain | None

    def __init__(self,
                 a_domain: Domain,
                 carriers: list[Domain],
                 c_domain: Domain | None,
                 modification_domains: list[Domain],
                 validate: bool = True, **kwargs) -> None:
        self.a_domain = a_domain
        self.c_domain = c_domain
        if c_domain:
            core = [c_domain, a_domain]
        else:
            core = [a_domain]
        super().__init__(carriers, modification_domains, core_domains=core, **kwargs)

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        new = cls(
            a_domain=Domain.from_json(raw.pop("a_domain"), **kwargs),
            carriers=[Domain.from_json(carrier, **kwargs) for carrier in raw.pop("carriers")],
            c_domain=Domain.from_json(raw.pop("c_domain"), **kwargs) if "c_domain" in raw else None,
            modification_domains=[Domain.from_json(domain, **kwargs) for domain in raw.pop("modification_domains", [])],
            **kwargs,
        )
        return new

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret.pop("core_domains")
        ret.update({
            "a_domain": self.a_domain.to_json(),
        })
        if self.c_domain:
            ret["c_domain"] = self.c_domain.to_json()
        return ret
