from typing import Any, Self

from .core import DomainInfo


class Carrier(DomainInfo):
    beta_branching: bool | None

    VALID_SUBTYPES = (
        "ACP",
        "PCP",
    )

    def __init__(self, subtype: str | None = None, beta_branching: bool | None = None, **kwargs) -> None:
        self.beta_branching = beta_branching
        super().__init__(subtype=subtype, **kwargs)

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            subtype=raw.get("subtype"),
            beta_branching=raw.get("beta_branching"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.beta_branching is not None:
            ret["beta_branching"] = self.beta_branching

        return ret
