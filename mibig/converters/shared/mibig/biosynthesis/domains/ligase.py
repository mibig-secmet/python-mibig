from typing import Any, Self

from mibig.converters.shared.common import QualityLevel, Smiles
from mibig.converters.shared.mibig.common import SubstrateEvidence
from mibig.errors import ValidationErrorInfo

from .core import DomainInfo


class Ligase(DomainInfo):
    substrates: list[Smiles]
    evidence: list[SubstrateEvidence]

    def __init__(self, substrates: list[Substrate], evidence: list[SubstrateEvidence], **kwargs) -> None:
        super().__init__(substrates=substrates, evidence=evidence, **kwargs)

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            substrates=[Substrate(sub, Smiles(sub)) for sub in raw.get("substrates", [])],
            evidence=[SubstrateEvidence.from_json(evi, **kwargs) for evi in raw.get("evidence", [])],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        ret.update({
            "substrates": [sub.to_json()["smiles"] for sub in self.substrates],
            "evidence": [evi.to_json() for evi in self.evidence],
        })
        return ret
