from typing import Any, Self

from mibig.converters.shared.common import Smiles, Citation, validate_citation_list
from mibig.errors import ValidationError, ValidationErrorInfo

from .steps import parse_step, format_step

class Product:
    name: str
    structure: Smiles | None
    comment: str | None

    def __init__(self, name: str, structure: Smiles | None, comment: str | None, validate: bool = True):
        self.name = name
        self.structure = structure
        self.comment = comment

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []

        if not self.name:
            errors.append(ValidationErrorInfo("Product.name", "Missing name"))

        if self.structure:
            errors.extend(self.structure.validate())

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            name=raw["name"],
            structure=Smiles(raw["structure"]) if "structure" in raw else None,
            comment=raw.get("comment"),
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "name": self.name,
        }
        if self.structure:
            ret["structure"] = self.structure.to_json()
        if self.comment:
            ret["comment"] = self.comment

        return ret


class Path:
    products: list[Product]
    steps: list[tuple[str, ...]]
    references: list[Citation]
    is_subcluster: bool
    produces_precursor: bool

    def __init__(self, products: list[Product],
                 steps: list[tuple[str, ...]],
                 references: list[Citation],
                 is_subcluster: bool,
                 produces_precursor: bool,
                 validate: bool = True):
        self.products = products
        self.steps = steps
        self.references = references
        self.is_subcluster = is_subcluster
        self.produces_precursor = produces_precursor

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors = []

        if not self.products:
            errors.append(ValidationErrorInfo("Path.products", "Missing products"))

        errors.extend(validate_citation_list(self.references))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        steps = parse_step(raw["steps"])
        return cls(
            products=[Product.from_json(product) for product in raw["products"]],
            steps=steps,
            references=[Citation.from_json(ref) for ref in raw["references"]],
            is_subcluster=raw["isSubcluster"],
            produces_precursor=raw["producesPrecursor"],
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "products": [product.to_json() for product in self.products],
            "steps": format_step(self.steps),
            "references": [ref.to_json() for ref in self.references],
            "isSubcluster": self.is_subcluster,
            "producesPrecursor": self.produces_precursor,
        }
