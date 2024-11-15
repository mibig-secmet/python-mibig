from dataclasses import dataclass, InitVar
import datetime
from enum import Enum
from functools import total_ordering
import re
from typing import Any, Self

from mibig.errors import ValidationError
from mibig.validation import ValidationErrorInfo
from mibig.utils import CDS, INVALID_CHARS, Record


@total_ordering
class QualityLevel(Enum):
    QUESTIONABLE = "questionable"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def __lt__(self, other: Self) -> bool:
        if self.__class__ != other.__class__:
            return NotImplemented

        values = list(self.__class__)

        return values.index(self) < values.index(other)


class StatusLevel(Enum):
    PENDING = "pending"
    EMBARGOED = "embargoed"
    ACTIVE = "active"
    RETIRED = "retired"


class Location:
    begin: int
    end: int

    def __init__(self, begin: int, end: int, validate: bool = True, **kwargs) -> None:
        self.begin = begin
        self.end = end

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        begin = raw["from"]
        end = raw["to"]
        if not isinstance(begin, int):
            raise ValueError("Location.from needs to be an integer")
        if not isinstance(end, int):
            raise ValueError("Location.to needs to be an integer")

        return cls(begin, end, **kwargs)

    def to_json(self) -> dict[str, int]:
        return {"from": self.begin, "to": self.end}

    def validate(
        self,
        record: Record | None = None,
        cds: CDS | None = None,
        quality: QualityLevel | None = None,
        **kwargs,
    ) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if self.begin < 0 and quality != QualityLevel.QUESTIONABLE:
            errors.append(
                ValidationErrorInfo("Location.from", "From coordinate must be positive")
            )
        if self.end < 0 and quality != QualityLevel.QUESTIONABLE:
            errors.append(
                ValidationErrorInfo("Location,to", "To coordinate must be positive")
            )

        if self.begin > self.end:
            errors.append(
                ValidationErrorInfo(
                    "Location",
                    f"Location.from {self.begin} must be less than Location.to {self.end}",
                )
            )

        if record and not quality == QualityLevel.QUESTIONABLE:
            if self.begin > record.seq_len:
                errors.append(
                    ValidationErrorInfo(
                        "Location.from",
                        "Location.from must be less than the sequence length",
                    )
                )
            if self.end > record.seq_len:
                errors.append(
                    ValidationErrorInfo(
                        "Location.to",
                        "Location.to must be less than the sequence length",
                    )
                )

        if cds:
            if self.end > cds.translation_length:
                errors.append(
                    ValidationErrorInfo(
                        "Location.to",
                        "Location.to must be less than the translation length",
                    )
                )
        return errors


class NovelGeneId:
    _inner: str

    def __init__(self, inner: str, validate: bool = True, **kwargs) -> None:
        self._inner = inner

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self._inner

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if not self._inner:
            errors.append(ValidationErrorInfo("gene_id", "Gene id cannot be empty"))

        quality: QualityLevel | None = kwargs.get("quality")
        if quality == QualityLevel.QUESTIONABLE:
            multi_locus_name = re.match(
                r"^(\w{3,4})\([\d\w._]+:\d+\-\d+\)$", self._inner
            )
            if multi_locus_name:
                if INVALID_CHARS.search(multi_locus_name.group(1)):
                    errors.append(
                        ValidationErrorInfo(
                            "gene_id",
                            f"Gene id {self._inner!r} contains invalid characters",
                        )
                    )
                return errors

        if INVALID_CHARS.search(self._inner):
            errors.append(
                ValidationErrorInfo(
                    "gene_id",
                    f"Gene id {self._inner!r} contains invalid characters",
                )
            )

        return errors

    @classmethod
    def from_json(cls, raw: str, **kwargs) -> Self:
        return cls(raw, **kwargs)

    def to_json(self) -> str:
        return self._inner

    def __lt__(self, other: Self) -> bool:
        return self._inner < other._inner


class GeneId(NovelGeneId):
    def validate(
        self, record: Record | None = None, **kwargs
    ) -> list[ValidationErrorInfo]:
        errors = super().validate(**kwargs)

        if record and not record.get_cds(self._inner):
            errors.append(
                ValidationErrorInfo(
                    "gene_id", f"Gene id {self._inner!r} not found in record"
                )
            )

        return errors


_UNIQUE_CITATIONS = {}  # for single-instance tracking, making numerical identifiers easier to manage

@total_ordering
class Citation:
    VALID_PATTERNS = {
        "pubmed": r"^(\d+)$",
        "doi": r"^10\.\d{4,9}/[-\._;()/:a-zA-Z0-9]+$",
        "patent": r"^(.+)$",
        "url": r"^https?:\/\/(www\\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)$",
    }
    database: str
    value: str

    def __new__(cls, database: str, value: str, validate: bool = True, short_id: str = "") -> None:
        instance = _UNIQUE_CITATIONS.get((database, value))
        if not instance:
            instance = super().__new__(cls)
            _UNIQUE_CITATIONS[(database, value)] = instance
        return instance

    def __init__(self, database: str, value: str, validate: bool = True, short_id: str = "") -> None:
        self.database = database
        self.value = value
        self.short_id = short_id

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def to_json(self) -> str:
        return f"{self.database}:{self.value}"

    def to_url(self):
        if not self.short_id:
            raise
        if self.database == "pubmed":
            return f"https://www.ncbi.nlm.nih.gov/pubmed/{self.value}"
        if self.database == "doi":
            return f"https://dx.doi.org/{self.value}"
        if self.database == "patent":
            return f"https://patents.google.com/patent/{self.value}"
        if self.database == "url":
            return self.value
        raise NotImplementedError(f"unhandled database type: {self.database}")

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

    def __lt__(self, other: Self) -> bool:
        return (self.database, self.value) < (other.database, other.value)

    def __hash__(self) -> int:
        return hash((self.database, self.value))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Citation):
            return False
        return other.database == self.database and other.value == self.value

    def __repr__(self) -> str:
        return f"Citation({self.database=}, {self.value=}, {self.short_id=})"


class Evidence:
    method: str
    references: list[Citation]

    VALID_METHODS = {
        "Sequence-based prediction",
    }

    def __init__(self, method: str, references: list[Citation], validate: bool = True, **kwargs) -> None:
        self.method = method
        self.references = list(set(references))

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, quality: QualityLevel | None = None) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if self.method not in self.VALID_METHODS:
            errors.append(
                ValidationErrorInfo(
                    f"{type(self)}.method", f"Invalid method {self.method!r}"
                )
            )

        if self.method != "Sequence-based prediction":
            errors.extend(validate_citation_list(self.references, f"{type(self)}.references", quality=quality))

        return errors

    def to_json(self) -> dict[str, Any]:
        ret: dict[str, Any] = {
            "method": self.method,
        }

        if self.references:
            ret["references"] = [r.to_json() for r in self.references]

        return ret

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        method = raw["method"]
        references = [Citation.from_json(r) for r in raw.get("references", [])]
        return cls(method, references, **kwargs)


def validate_citation_list(
    citations: list[Citation],
    field: str | None = None,
    quality: QualityLevel | None = None,
) -> list[ValidationErrorInfo]:
    if field is None:
        field = "Citation"

    errors: list[ValidationErrorInfo] = []
    if quality is not QualityLevel.QUESTIONABLE and not citations:
        errors.append(
            ValidationErrorInfo(
                field, f"citation list cannot be empty at quality level {quality}"
            )
        )
    for citation in citations:
        errors.extend(citation.validate())
    return errors


@dataclass(frozen=True)
class SubmitterID:
    _inner: str
    _validate: InitVar[bool] = True

    def __post_init__(self, _validate: bool = True) -> None:
        if not _validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def __lt__(self, other: Self) -> bool:
        return self._inner < other._inner

    def validate(self) -> list[ValidationErrorInfo]:
        if len(self._inner) != 24:
            return [ValidationErrorInfo("submitter", "invalid length")]

        if not self._inner.isalnum():
            return [ValidationErrorInfo("submitter", "invalid characters")]

        return []

    def __str__(self) -> str:
        return self._inner

    def to_json(self) -> str:
        return self._inner

    @classmethod
    def from_json(cls, raw: str) -> Self:
        return cls(raw)


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
        **kwargs,
    ) -> None:
        self.contributors = contributors
        self.reviewers = reviewers
        self.date = date
        self.comment = comment

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []
        quality: QualityLevel | None = kwargs.get("quality")
        if not self.contributors:
            errors.append(
                ValidationErrorInfo("contributors", "contributor list cannot be empty")
            )
        if quality != QualityLevel.QUESTIONABLE and not self.reviewers:
            errors.append(
                ValidationErrorInfo("reviewers", "reviewer list cannot be empty")
            )
        for contributor in self.contributors:
            errors.extend(contributor.validate())
        for reviewer in self.reviewers:
            errors.extend(reviewer.validate())

        return errors

    def __str__(self) -> str:
        return f"{self.date} {self.comment}, Contributors: {', '.join(str(c) for c in self.contributors)}; Reviewers: {', '.join(str(r) for r in self.reviewers)}"

    def to_json(self) -> dict[str, Any]:
        return {
            "contributors": [c.to_json() for c in self.contributors],
            "reviewers": [r.to_json() for r in self.reviewers],
            "date": self.date.strftime("%Y-%m-%d"),
            "comment": self.comment,
        }

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        contributors = [SubmitterID.from_json(c) for c in raw.get("contributors", [])]
        reviewers = [SubmitterID.from_json(r) for r in raw.get("reviewers", [])]
        date = datetime.datetime.strptime(raw["date"], "%Y-%m-%d")
        comment = raw["comment"]
        return cls(contributors, reviewers, date, comment, **kwargs)


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

    def __str__(self) -> str:
        return self._inner

    def to_json(self) -> str:
        return self._inner

    @classmethod
    def from_json(cls, raw: str) -> Self:
        return cls(raw)


class Release:
    version: ReleaseVersion
    date: datetime.date | None
    entries: list[ReleaseEntry]

    def __init__(
        self,
        version: ReleaseVersion,
        date: datetime.date | None,
        entries: list[ReleaseEntry],
        validate: bool = True,
        **kwargs,
    ) -> None:
        self.version = version
        self.date = date
        self.entries = entries

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        errors.extend(self.version.validate())

        if self.date is None and str(self.version) != "next":
            errors.append(
                ValidationErrorInfo(
                    "Release", "Release date must be provided if version is not 'next'"
                )
            )

        for entry in self.entries:
            errors.extend(entry.validate(**kwargs))

        return errors

    def __str__(self) -> str:
        ret = f"{self.version} ({self.date})\n"
        for entry in self.entries:
            ret += f"  {entry}\n"

        return ret

    def to_json(self) -> dict[str, Any]:
        ret = {
            "version": self.version.to_json(),
            "entries": [e.to_json() for e in self.entries],
        }
        ret["date"] = self.date.strftime("%Y-%m-%d") if self.date else None
        return ret

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        version = ReleaseVersion.from_json(raw["version"])
        date = (
            datetime.datetime.strptime(raw["date"], "%Y-%m-%d") if raw["date"] else None
        )
        entries = [ReleaseEntry.from_json(e, **kwargs) for e in raw["entries"]]

        return cls(version, date, entries, **kwargs)


class ChangeLog:
    releases: list[Release]

    def __init__(self, releases: list[Release], validate: bool = True, **kwargs) -> None:
        self.releases = releases

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, **kwargs) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        for release in self.releases:
            errors.extend(release.validate(**kwargs))

        return errors

    def __str__(self) -> str:
        return "\n".join(str(r) for r in self.releases)

    def to_json(self) -> dict[str, Any]:
        return {"releases": [r.to_json() for r in self.releases]}

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        releases = [Release.from_json(r, **kwargs) for r in raw["releases"]]
        return cls(releases, **kwargs)


class Smiles:
    value: str

    def __init__(self, value: str, validate: bool = True) -> None:
        self.value = value

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if not re.match(r"^[\[\]a-zA-Z0-9\@()=\/\\#+.%*-]+$", self.value):
            errors.append(
                ValidationErrorInfo("Smiles", f"Invalid value {self.value!r}")
            )

        return errors

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_json(cls, raw: str) -> Self:
        return cls(raw)

    def to_json(self) -> str:
        return self.value
