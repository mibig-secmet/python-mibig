from .core import ActiveDomain


class Other(ActiveDomain):
    def __init__(self, subtype: str, **kwargs) -> None:  # subtypes are not optional here
        super().__init__(subtype=subtype, **kwargs)
