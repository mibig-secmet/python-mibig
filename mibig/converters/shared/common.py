from dataclasses import dataclass
import datetime
import re
from typing import Any, Self


from mibig.errors import ValidationError
from mibig.validation import ValidationErrorInfo


@dataclass
class Location:
    begin: int
    end: int

    def __post_init__(self) -> None:
        if self.begin < self.end:
            raise ValueError("Location.to cannot be smaller than Location.from")

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        begin = raw["from"]
        end = raw["to"]
        if not isinstance(begin, int):
            raise ValueError("Location.from needs to be an integer")
        if not isinstance(end, int):
            raise ValueError("Location.to needs to be an integer")

        return cls(begin, end)

    def to_json(self) -> dict[str, int]:
        return {"from": self.begin, "to": self.end}

    def validate(self, **_kwargs) -> list[ValidationErrorInfo]:
        # TODO: Add when sequence handling has been decided
        raise NotImplementedError


class GeneId:
    _inner: str

    def __init__(self, inner: str) -> None:
        if " " in inner or "," in inner:
            raise ValueError(f"Invalid gene id {inner!r}")

        self._inner = inner

    def __str__(self) -> str:
        return self._inner

    def to_json(self) -> str:
        return self._inner

    def validate(self, **_kwargs) -> list[ValidationErrorInfo]:
        # TODO: Add when sequence handing has been decided
        raise NotImplementedError


class Citation:
    VALID_PATTERNS = {
        "pubmed": r"^(\d+)$",
        "doi": r"^10\.\d{4,9}/[-\._;()/:a-zA-Z0-9]+$",
        "patent": r"^(.+)$",
        "url": r"^https?:\/\/(www\\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$",
    }
    database: str
    value: str

    def __init__(self, database: str, value: str) -> None:
        self.database = database
        self.value = value
        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def to_json(self) -> str:
        return f"{self.database}:{self.value}"

    @classmethod
    def from_json(cls, raw: str) -> Self:
        database, value = raw.split(":", 1)
        return cls(database, value)

    def validate(self) -> list[ValidationErrorInfo]:
        if self.database not in self.VALID_PATTERNS.keys():
            return [
                ValidationErrorInfo(
                    "citation", f"Invalid database type {self.database!r}"
                )
            ]

        if not re.match(self.VALID_PATTERNS[self.database], self.value):
            return [
                ValidationErrorInfo(
                    "citation",
                    f"Invalid value {self.value!r} for database {self.database!r}",
                )
            ]
        return []


class SubmitterID:
    _inner: str

    def __init__(self, value: str, validate: bool = True) -> None:
        self._inner = value

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        if len(self._inner) != 24:
            return [ValidationErrorInfo("submitter", "invalid length")]

        if not self._inner.isalnum():
            return [ValidationErrorInfo("submitter", "invalid characters")]

        return []

    def to_json(self) -> str:
        return self._inner

    @classmethod
    def from_json(cls, raw: str) -> Self:
        return cls(raw, validate=True)


class ReleaseEntry:
    contributors: list[SubmitterID]
    reviewers: list[SubmitterID]
    date: datetime.date
    comment: str

    def __init__(
        self,
        contributors: list[SubmitterID],
        reviewers: list[SubmitterID],
        date: datetime.date,
        comment: str,
        validate: bool = True,
    ) -> None:
        self.contributors = contributors
        self.reviewers = reviewers
        self.date = date
        self.comment = comment

        if not validate:
            return

        self.validate()

    def validate(self) -> list[ValidationErrorInfo]:
        raise NotImplementedError


class ReleaseVersion:
    _inner: str

    def __init__(self, value: str, validate: bool = True) -> None:
        self._inner = value

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        if self._inner == "next":
            return []

        for part in self._inner.split("."):
            if not part.isdigit():
                return [
                    ValidationErrorInfo(
                        "release version", f"invalid version {self._inner!r}"
                    )
                ]
        return []


class Release:
    version: ReleaseVersion
    date: datetime.date
