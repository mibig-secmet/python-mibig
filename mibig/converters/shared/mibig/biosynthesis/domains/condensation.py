from mibig.converters.shared.common import validate_citation_list
from mibig.errors import ValidationErrorInfo


from .core import DomainInfo


class Condensation(DomainInfo):
    VALID_SUBTYPES = (
        "Dual",
        "Starter",
        "LCL",
        "DCL",
        "Ester bond-forming",
        "Heterocyclization",
    )

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors = []
        if self.subtype:
            errors.extend(validate_citation_list(self.references, f"{type(self)}.references", **kwargs))
        return errors
