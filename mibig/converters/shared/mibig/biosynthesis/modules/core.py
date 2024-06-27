from itertools import chain
from typing import Any, Iterator, Self

from mibig.converters.shared.mibig.biosynthesis.domains.base import Domain
from mibig.errors import ValidationError, ValidationErrorInfo


class ModuleInfo:
    carriers: list[Domain]
    modification_domains: list[Domain]
    core_domains: list[Domain] = None

    def __init__(self,
                 carriers: list[Domain] = None,
                 modification_domains: list[Domain] = None,
                 core_domains: list[Domain] = None,
                 validate: bool = True, **kwargs) -> None:
        self.carriers = carriers or []
        self.modification_domains = modification_domains or []
        self.core_domains = core_domains or []

        if not validate:
            return

        errors = self._validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def _validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        domains = self.get_domains()
        if not domains:
            errors.append(ValidationErrorInfo(f"{type(self)}.references", "Modules require at least one domain"))
        for domain in domains:
            errors.extend(domain.validate(**kwargs))
        errors.extend(self.validate(**kwargs))
        return errors

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        return []

    def get_domains(self) -> Iterator[Domain]:
        return chain(self.core_domains, self.modification_domains, self.carriers)

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        new = cls(
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
        ret = {
            "carriers": [carrier.to_json() for carrier in self.carriers],
        }

        if self.modification_domains:
            ret["modification_domains"] = [
                domain.to_json() for domain in self.modification_domains
            ]
        if self.core_domains:
            ret["core_domains"] = [
                domain.to_json() for domain in self.core_domains
            ]
        return ret
