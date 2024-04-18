from typing import Any, Self

from mibig.converters.shared.common import GeneId
from mibig.converters.shared.mibig.biosynthesis.classes import BiosynthesisClass
from mibig.converters.shared.mibig.biosynthesis.modules.base import Module
from mibig.converters.shared.mibig.biosynthesis.path import Path
from mibig.errors import ValidationError, ValidationErrorInfo


class Biosynthesis:
    classes: list[BiosynthesisClass]
    modules: list[Module]
    operons: list[list[GeneId]]
    paths: list[Path]

    def __init__(self,
                 classes: list[BiosynthesisClass],
                 modules: list[Module],
                 operons: list[list[GeneId]],
                 paths: list[Path],
                 validate: bool = True, **kwargs) -> None:
        self.classes = classes
        self.modules = modules
        self.operons = operons
        self.paths = paths

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        if not self.classes:
            errors.append(ValidationErrorInfo("Biosynthesis.classes", "At least one class is required"))
        if not self.paths:
            errors.append(ValidationErrorInfo("Biosynthesis.paths", "At least one path is required"))

        for _class in self.classes:
            errors.extend(_class.validate(**kwargs))
        for module in self.modules:
            errors.extend(module.validate(**kwargs))
        for operons in self.operons:
            for operon in operons:
                errors.extend(operon.validate(**kwargs))
        for path in self.paths:
            errors.extend(path.validate())
        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        operons_list = []
        for operons in raw.get("operons", []):
            operons_list.append([GeneId.from_json(gene, **kwargs) for gene in operons])
        return cls(
            classes=[BiosynthesisClass.from_json(cls) for cls in raw["classes"]],
            modules=[Module.from_json(module, **kwargs) for module in raw.get("modules", [])],
            operons=operons_list,
            paths=[Path.from_json(path) for path in raw["paths"]],
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "classes": [cls.to_json() for cls in self.classes],
        }

        if self.modules:
            ret["modules"] = [module.to_json() for module in self.modules]

        if self.operons:
            operons_list = []
            for operons in self.operons:
                operons_list.append([gene.to_json() for gene in operons])
            ret["operons"] = operons_list

        if self.paths:
            ret["paths"] = [path.to_json() for path in self.paths]

        return ret
