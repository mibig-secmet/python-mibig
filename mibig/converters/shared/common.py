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

    def __init__(self, database: str, value: str, validate: bool = True) -> None:
        self.database = database
        self.value = value

        if not validate:
            return

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


def validate_citation_list(citations: list[Citation], field: str | None = None) -> list[ValidationErrorInfo]:
    if field is None:
        field = "Citation"

    errors: list[ValidationErrorInfo] = []
    if not citations:
        errors.append(ValidationErrorInfo(field, "citation list cannot be empty"))
    for citation in citations:
        errors.extend(citation.validate())
    return errors


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

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []
        if not self.contributors:
            errors.append(
                ValidationErrorInfo("contributors", "contributor list cannot be empty")
            )
        for contributor in self.contributors:
            errors.extend(contributor.validate())
        for reviewer in self.reviewers:
            errors.extend(reviewer.validate())

        return errors

    def to_json(self) -> dict[str, Any]:
        return {
            "contributors": [c.to_json() for c in self.contributors],
            "reviewers": [r.to_json() for r in self.reviewers],
            "date": self.date.strftime("%Y-%m-%d"),
            "comment": self.comment,
        }

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        contributors = [SubmitterID.from_json(c) for c in raw.get("contributors", [])]
        reviewers = [SubmitterID.from_json(r) for r in raw.get("reviewers", [])]
        date = datetime.datetime.strptime(raw["date"], "%Y-%m-%d")
        comment = raw["comment"]
        return cls(contributors, reviewers, date, comment)


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

    def to_json(self) -> str:
        return self._inner

    @classmethod
    def from_json(cls, raw: str) -> Self:
        return cls(raw)


class Release:
    version: ReleaseVersion
    date: datetime.date
    entries: list[ReleaseEntry]

    def __init__(
        self,
        version: ReleaseVersion,
        date: datetime.date,
        entries: list[ReleaseEntry],
        validate: bool = True,
    ) -> None:
        self.version = version
        self.date = date
        self.entries = entries

        if not validate:
            return

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        errors.extend(self.version.validate())
        for entry in self.entries:
            errors.extend(entry.validate())

        return errors

    def to_json(self) -> dict[str, Any]:
        return {
            "version": self.version.to_json(),
            "date": self.date.strftime("%Y-%m-%d"),
            "entries": [e.to_json() for e in self.entries],
        }

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        version = ReleaseVersion.from_json(raw["version"])
        date = datetime.datetime.strptime(raw["date"], "%Y-%m-%d")
        entries = [ReleaseEntry.from_json(e) for e in raw["entries"]]

        return cls(version, date, entries)


class ChangeLog:
    releases: list[Release]

    def __init__(self, releases: list[Release], validate: bool = True) -> None:
        self.releases = releases

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        for release in self.releases:
            errors.extend(release.validate())

        return errors

    def to_json(self) -> dict[str, Any]:
        return {"releases": [r.to_json() for r in self.releases]}

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        releases = [Release.from_json(r) for r in raw["releases"]]
        return cls(releases)
