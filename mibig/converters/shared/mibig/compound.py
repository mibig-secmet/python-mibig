import re
from typing import Any, Self

from mibig.converters.shared.common import Citation, Smiles, validate_citation_list
from mibig.converters.shared.mibig.common import QualityLevel
from mibig.errors import ValidationError
from mibig.validation import ValidationErrorInfo


class Assay:
    concentration: str
    target: str

    def __init__(self, concentration: str, target: str, validate: bool = True) -> None:
        self.concentration = concentration
        self.target = target

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if not self.concentration:
            errors.append(ValidationErrorInfo("Assay", "Missing concentration"))

        if not self.target:
            errors.append(ValidationErrorInfo("Assay", "Missing target"))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(raw["concentration"], raw["target"])

    def to_json(self) -> dict[str, Any]:
        return {"concentration": self.concentration, "target": self.target}


class Bioactivity:
    name: str
    observed: bool
    references: list[Citation]
    assays: list[Assay] | None

    def __init__(self, name: str, observed: bool, references: list[Citation],
                 assays: list[Assay] | None = None, validate: bool = True) -> None:
        self.name = name
        self.observed = observed
        self.references = references
        self.assays = assays

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if not self.name:
            errors.append(ValidationErrorInfo("Bioactivity", "Missing name"))

        if not self.references:
            errors.append(ValidationErrorInfo("Bioactivity", "Missing references"))

        errors.extend(validate_citation_list(self.references))

        if not self.assays:
            return errors

        for assay in self.assays:
            errors.extend(assay.validate())

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(
            raw["name"],
            raw["observed"],
            [Citation.from_json(c) for c in raw["references"]],
            assays=[Assay.from_json(a) for a in raw.get("assays", [])],
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "name": self.name,
            "observed": self.observed,
            "references": [r.to_json() for r in self.references],
        }
        if self.assays:
            ret["assays"] = [a.to_json() for a in self.assays]

        return ret


class CompoundClass:
    value: str

    VALID_CLASSES = {
        "Alkaloid": (
            "Amination reaction-derived",
            "Anthranilic acid-derived",
            "Arginine-derived",
            "Guanidine-derived",
            "Histidine-derived",
            "Lysine-derived",
            "Nicotinic acid-derived",
            "Ornithine-derived",
            "Peptide alkaloid",
            "Proline-derived",
            "Purine alkaloid",
            "Serine-derived",
            "Steroidal alkaloid",
            "Tetramate alkaloid",
            "Terpenoid-alkaloid",
            "Tryptophan-derived",
            "Tyrosine-derived",
        ),
        "Shikimic acid-derived": (
            "Aromatic amino acid/simple benzoic acid",
            "Aromatic polyketide",
            "Phenylpropanoid",
            "Terpenoid quinone",
        ),
        "Acetate-derived": (
            "Alkylresorcinol/phloroglucinol polyketide",
            "Chromane polyketide",
            "Cyclic polyketide",
            "Fatty acid",
            "Fatty acid derivate",
            "Linear polyketide",
            "Macrocyclic polyketide",
            "Naphthalene polyketide",
            "Polycyclic polyketide",
            "Polyether polyketide",
            "Xanthone polyketide",
        ),
        "Isoprene-derived": (
            "Atypical terpenoid",
            "Diterpenoid",
            "Hemiterpenoid",
            "Higher terpenoid",
            "Iridoid",
            "Meroterpenoid",
            "Monoterpenoid",
            "Sesquiterpenoid",
            "Steroid",
        ),
        "Peptide": (
            "Beta-lactam",
            "Depsipeptide",
            "Diketopiperazine",
            "Glycopeptide",
            "Glycopeptidolipid",
            "Linear",
            "Lipopeptide",
            "Macrocyclic",
        ),
        "Carbohydrates": (
            "Monosaccharide",
            "Oligosaccharide",
            "Polysaccharide",
            "Nucleoside",
            "Aminoglycoside",
            "Liposaccharide",
            "Glucosinolate",
        ),
        "Glycolysis-derived": (
            "Butenolide",
            "Butyrolactone",
            "Tetronic acid",
        ),
        "Other": (
            "Lactone",
            "Ectoine",
            "Furan",
            "Phosphonate",
        ),
    }

    def __init__(self, value: str, validate: bool = True) -> None:
        self.value = value

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        for _, subclasses in self.VALID_CLASSES.items():
            if self.value in subclasses:
                return []

        errors.append(
            ValidationErrorInfo(
                message=f"Invalid compound class: {self.value}",
                field="compound.class",
            )
        )

        return errors

    @classmethod
    def from_json(cls, raw: str) -> Self:
        return cls(raw)

    def to_json(self) -> str:
        return self.value


class Evidence:
    method: str
    references: list[Citation]

    VALID_METHODS = (
        "NMR",
        "Mass spectrometry",
        "MS/MS",
        "X-ray cristallography",
        "Chemical derivatisation",
        "Total synthesis",
    )

    def __init__(self, method: str, references: list[Citation], validate: bool = True) -> None:
        self.method = method
        self.references = references

        if not validate:
            return

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if self.method not in self.VALID_METHODS:
            errors.append(
                ValidationErrorInfo(
                    message=f"Invalid method: {self.method}",
                    field="compound.evidence.method",
                )
            )

        errors.extend(validate_citation_list(self.references))

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any]) -> Self:
        return cls(raw["method"], [Citation.from_json(c) for c in raw["references"]])

    def to_json(self) -> dict[str, Any]:
        return {"method": self.method, "references": [r.to_json() for r in self.references]}


VALID_NAME_PATTERN = r"^[a-zA-Zα-ωΑ-Ω0-9\[\]'()\/&,. +-]+$"

class CompoundRef:
    database: str
    identifier: str

    VALID_DATABASE_PATTERNS = {
        "pubchem": r"^\d+$",
        "chebi": r"^\d+$",
        "chembl": r"^CHEMBL\d+$",
        "chemspider": r"^\d+$",
        "npatlas": r"^NPA\d+$",
        "lotus": r"^Q\d+$",
        "gnps": r"^MSV\d+$",
        "cyanometdb": r"^CyanoMetDB_\d{4,4}$",
    }

    def __init__(self, database: str, identifier: str, validate: bool = True) -> None:
        self.database = database
        self.identifier = identifier

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if self.database not in self.VALID_DATABASE_PATTERNS:
            errors.append(
                ValidationErrorInfo(
                    message=f"Invalid database: {self.database}",
                    field="compound.database",
                )
            )

        if not re.match(self.VALID_DATABASE_PATTERNS[self.database], self.identifier):
            errors.append(
                ValidationErrorInfo(
                    message=f"Invalid identifier: {self.identifier}",
                    field="compound.database",
                )
            )

        return errors

    @classmethod
    def from_json(cls, raw: str) -> Self:
        database, identifier = raw.split(":", 1)
        return cls(database, identifier)

    def to_json(self) -> str:
        return f"{self.database}:{self.identifier}"


FORMULA_PARTS_PATTERN = re.compile(r"([A-Z][a-z]?)([0-9]*)")


class FormulaPart:
    atom: str
    count: int

    def __init__(self, atom: str, count: int, validate: bool = True) -> None:
        self.atom = atom
        self.count = count

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if not re.match(r"^[A-Za-z]+$", self.atom):
            errors.append(
                ValidationErrorInfo(
                    message=f"Invalid atom: {self.atom}",
                    field="compound.formula",
                )
            )

        if self.count <= 0:
            errors.append(
                ValidationErrorInfo(
                    message=f"Invalid count: {self.count}",
                    field="compound.formula",
                )
            )

        return errors


class Formula:
    raw: str
    _parts: list[FormulaPart]

    def __init__(self, raw: str, validate: bool = True):
        self.raw = raw
        self._parts = self._parse(raw)

        if not validate:
            return

        errors = self.validate()
        if errors:
            raise ValidationError(errors)

    def validate(self) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []
        for part in self._parts:
            errors.extend(part.validate())

        return errors

    @property
    def parts(self) -> list[FormulaPart]:
        return self._parts

    @staticmethod
    def _parse(raw: str) -> list[FormulaPart]:
        raw_parts = FORMULA_PARTS_PATTERN.findall(raw)
        parts: list[FormulaPart] = []
        for atom, count in raw_parts:
            if not count:
                count = "1"
            parts.append(FormulaPart(atom, int(count)))
        return parts

    @classmethod
    def from_json(cls, raw: str) -> Self:
        return cls(raw)

    def to_json(self) -> str:
        return self.raw


class Compound:
    name: str
    evidence: list[Evidence]
    classes: list[CompoundClass]
    bioactivities: list[Bioactivity]
    structure: Smiles | None
    synonyms: list[str]
    databases: list[CompoundRef]
    moieties: list[str]
    cyclic: bool | None
    mass: float | None
    formula: Formula | None

    def __init__(self, name: str,
                 evidence: list[Evidence],
                 classes: list[CompoundClass] | None = None,
                 bioactivities: list[Bioactivity] | None = None,
                 structure: Smiles | None = None,
                 synonyms: list[str] | None = None,
                 databases: list[CompoundRef] | None = None,
                 moieties: list[str] | None = None,
                 cyclic: bool | None = None,
                 mass: float | None = None,
                 formula: Formula | None = None,
                 validate: bool = True,
                 **kwargs,
                ) -> None:
        self.name = name
        self.evidence = evidence
        self.classes = classes or []
        self.bioactivities = bioactivities or []
        self.structure = structure
        self.synonyms = synonyms or []
        self.databases = databases or []
        self.moieties = moieties or []
        self.cyclic = cyclic
        self.mass = mass
        self.formula = formula

        if not validate:
            return

        errors = self.validate(**kwargs)
        if errors:
            raise ValidationError(errors)

    def validate(self, quality: QualityLevel | None = None) -> list[ValidationErrorInfo]:
        errors: list[ValidationErrorInfo] = []

        if not re.match(VALID_NAME_PATTERN, self.name):
            errors.append(ValidationErrorInfo("Compound", f"Invalid name {self.name!r}"))

        if quality and quality is not QualityLevel.QUESTIONABLE:
            if not self.evidence:
                errors.append(ValidationErrorInfo("Compound", "Missing evidence"))

        for ev in self.evidence:
            errors.extend(ev.validate(quality=quality))

        for compound_class in self.classes:
            errors.extend(compound_class.validate())

        for bioactivity in self.bioactivities:
            errors.extend(bioactivity.validate())

        if self.structure is not None:
            errors.extend(self.structure.validate())

        for synonym in self.synonyms:
            if not re.match(VALID_NAME_PATTERN, synonym):
                errors.append(ValidationErrorInfo("Compound", f"Invalid synonym {synonym!r}"))

        for db in self.databases:
            errors.extend(db.validate())

        for moiety in self.moieties:
            if not re.match(VALID_NAME_PATTERN, moiety):
                errors.append(ValidationErrorInfo("Compound", f"Invalid moiety {moiety!r}"))

        if self.mass is not None and self.mass <= 0:
            errors.append(ValidationErrorInfo("Compound", f"Invalid mass {self.mass}"))

        if self.formula is not None:
            errors.extend(self.formula.validate())

        return errors

    @classmethod
    def from_json(cls, raw: dict[str, Any], **kwargs) -> Self:
        return cls(
            raw["name"],
            [Evidence.from_json(e, **kwargs) for e in raw["evidence"]],
            classes=[CompoundClass.from_json(c) for c in raw.get("classes", [])],
            bioactivities=[Bioactivity.from_json(b) for b in raw.get("bioactivities", [])],
            structure=Smiles.from_json(raw["structure"]) if "structure" in raw else None,
            synonyms=raw.get("synonyms"),
            databases=[CompoundRef.from_json(ref) for ref in raw.get("databaseIds", [])],
            moieties=raw.get("moieties"),
            cyclic=raw.get("cyclic"),
            mass=raw.get("mass"),
            formula=Formula.from_json(raw["formula"]) if "formula" in raw else None,
            **kwargs,
        )

    def to_json(self) -> dict[str, Any]:
        ret = {
            "name": self.name,
            "evidence": [e.to_json() for e in self.evidence],
        }
        if self.classes:
            ret["classes"] = [c.to_json() for c in self.classes]
        if self.bioactivities:
            ret["bioactivities"] = [b.to_json() for b in self.bioactivities]
        if self.structure:
            ret["structure"] = self.structure.to_json()
        if self.synonyms:
            ret["synonyms"] = self.synonyms
        if self.databases:
            ret["databaseIds"] = [db.to_json() for db in self.databases]
        if self.moieties:
            ret["moieties"] = self.moieties
        if self.cyclic:
            ret["cyclic"] = self.cyclic
        if self.mass:
            ret["mass"] = self.mass
        if self.formula:
            ret["formula"] = self.formula.to_json()

        return ret
