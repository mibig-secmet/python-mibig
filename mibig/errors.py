from mibig.validation import ValidationErrorInfo

class MibigError(RuntimeError):
    pass


class ValidationError(MibigError):
    info: list[ValidationErrorInfo]

    def __init__(self, info: list[ValidationErrorInfo]) -> None:
        super().__init__()
        self.info = info
