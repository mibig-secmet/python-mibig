from typing import Any, Self

from mibig.converters.shared.mibig.biosynthesis.domains.base import Domain

from .core import ModuleInfo


class CAL(ModuleInfo):
    cal: Domain

    def __init__(self, cal: Domain, carriers: list[Domain], modification_domains: list[Domain], validate: bool = True, **kwargs) -> None:
        self.cal = cal
        super().__init__(carriers=carriers, modification_domains=modification_domains, core_domains=[cal])

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        new = cls(
            cal=Domain.from_json(raw.pop("cal"), **kwargs),
            carriers=[Domain.from_json(domain, **kwargs) for domain in raw.pop("carriers", [])],
            modification_domains=[Domain.from_json(domain, **kwargs) for domain in raw.pop("modification_domains", [])],
            **kwargs,
        )
        assert not raw
        return new

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret["cal"] = ret.pop(ret["core_domains"][0])
        return ret
