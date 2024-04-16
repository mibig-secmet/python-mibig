from mibig.validation import ValidationErrorInfo

class MibigError(RuntimeError):
    pass


class ValidationError(MibigError):
    info: list[ValidationErrorInfo]

    def __init__(self, info: list[ValidationErrorInfo]) -> None:
        super().__init__()
        self.info = info

    def __str__(self) -> str:
        return "\n".join(str(e) for e in self.info)
