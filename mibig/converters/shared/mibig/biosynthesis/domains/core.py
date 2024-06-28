from typing import Any, Self

from mibig.converters.shared.common import Citation, Evidence, QualityLevel, Smiles, validate_citation_list
from mibig.errors import ValidationError, ValidationErrorInfo


class Substrate:
    name: str
    structure: Smiles | None

    VALID_NAMES = set()

    def __init__(self, name: str, structure: Smiles | None = None, validate: bool = True, **kwargs) -> None:
        self.name = name
        self.structure = structure

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        if not self.name:
            errors.append(
                ValidationErrorInfo(f"{type(self)}.name", "Missing name")
            )
        if self.VALID_NAMES and self.name not in self.VALID_NAMES:
            errors.append(
                ValidationErrorInfo(
                    f"{type(self)}.name", f"Invalid substrate name: {self.name}"
                )
            )
        return errors

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            name=raw["name"],
            structure=Smiles(raw["structure"]) if "structure" in raw else None,
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "name": self.name,
        }
        if self.structure:
            ret["structure"] = self.structure.to_json()
        return ret


class DomainInfo:
    subtype: str | None
    _references: list[Citation]
    evidence: list[Evidence]
    substrates: list[Substrate]

    VALID_SUBTYPES: tuple[str, ...] = tuple()

    def __init__(
        self, *,
        subtype: str | None = None,
        references: list[Citation] | None = None,
        evidence: list[Evidence] | None = None,
        substrates: list[Substrate] | None = None,
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.subtype = subtype
        self._references = references or []
        self.evidence = evidence or []
        self.substrates = substrates or []

        if not validate:
            return

        errors = self._validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    @property
    def references(self) -> list[Citation]:
        refs = list(self._references)
        for val in self.evidence:
            refs.extend(val.references)
        return refs

    def _validate(self, quality: QualityLevel = QualityLevel.QUESTIONABLE, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        if self.subtype and self.VALID_SUBTYPES and self.subtype not in self.VALID_SUBTYPES:
            errors.append(ValidationErrorInfo(f"{type(self)}.subtype", "invalid subtype"))
        if self.references or self.evidence:
            errors.extend(validate_citation_list(self.references, f"{type(self)}.references", quality=quality))
        for evidence in self.evidence:
            errors.extend(evidence.validate(quality=quality))
        for substrate in self.substrates:
            errors.extend(substrate.validate())

        if quality != QualityLevel.QUESTIONABLE:
            if self.substrates and not self.evidence:
                errors.append(ValidationErrorInfo(f"{type(self)}.references", "Substrates without evidence"))

        return errors + self.validate(quality=quality, **kwargs)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        return []

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            subtype=raw.pop("subtype", None),
            references=[Citation.from_json(ref) for ref in raw.get("references", [])],
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
        }
        if self.subtype:
            ret["subtype"] = self.subtype
        if self.references:
            ret["references"] = [ref.to_json() for ref in self.references]
        if self.substrates:
            ret["substrates"] = [sub.to_json() for sub in self.substrates]
        if self.evidence:
            ret["evidence"] = [ev.to_json() for ev in self.evidence]
        return ret


class ActiveDomain(DomainInfo):
    active: bool | None = None

    def __init__(self, *, active: bool | None = None, **kwargs) -> None:
        self.active = active
        super().__init__(**kwargs)

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            subtype=raw.get("subtype"),
            active=raw.get("active"),
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = super().to_json()
        if self.active is not None:
            ret["active"] = self.active
        return ret
