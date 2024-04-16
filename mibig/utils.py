import re
from typing import Self

from Bio.SeqRecord import SeqRecord
from helperlibs.bio import seqio

from mibig.errors import MibigError

INVALID_CHARS = re.compile(r"[!?,;:=+*&^%$#@ \t\n\r\\\/\[\]{}()<>|~`'\"]")


def _sanitise_identifier(identifier: str | None) -> str | None:
    if not identifier:
        return None

    return INVALID_CHARS.sub("", identifier)


class CDS:
    _locus_tag: str | None
    _gene: str | None
    _protein_id: str | None
    _translation: str | None
    _translation_length: int = 0

    def __init__(self, locus_tag: str | None = None, gene: str | None = None, protein_id: str | None = None, translation: str | None = None) -> None:
        if not any([locus_tag, gene, protein_id]):
            raise MibigError("At least one of locus_tag, gene, or protein_id is required")

        self._locus_tag = _sanitise_identifier(locus_tag)
        self._gene = _sanitise_identifier(gene)
        self._protein_id = _sanitise_identifier(protein_id)
        self.translation = translation

    @property
    def name(self) -> str:
        # make the type checker happy
        name = self._locus_tag or self._gene or self._protein_id
        assert name
        return name

    def has_name(self, name: str) -> bool:
        return name in [self._locus_tag, self._gene, self._protein_id]

    @property
    def translation_length(self) -> int:
        return self._translation_length

    @property
    def translation(self) -> str | None:
        return self._translation

    @translation.setter
    def translation(self, translation: str | None) -> None:
        self._translation = translation
        if not translation:
            return

        self._translation_length = len(translation)


class Record:
    id: str
    cdses: list[CDS]
    seq_len: int
    ncbi_tax_id: int | None
    organism: str | None
    _cds_by_locus: dict[str, CDS]
    _cds_by_gene: dict[str, CDS]
    _cds_by_protein: dict[str, CDS]

    def __init__(self, id: str, cdses: list[CDS], seq_len: int, ncbi_tax_id: int | None = None, organism: str | None = None) -> None:
        self.id = id
        self.cdses = cdses
        self.seq_len = seq_len
        self.ncbi_tax_id = ncbi_tax_id
        self.organism = organism

        self._cds_by_locus = {}
        self._cds_by_gene = {}
        self._cds_by_protein = {}
        for cds in cdses:
            if cds._locus_tag:
                self._cds_by_locus[cds._locus_tag] = cds
            if cds._gene:
                self._cds_by_gene[cds._gene] = cds
            if cds._protein_id:
                self._cds_by_protein[cds._protein_id] = cds

    def get_cds(self, name: str) -> CDS | None:
        return self._cds_by_locus.get(name) or self._cds_by_gene.get(name) or self._cds_by_protein.get(name)

    def has_cds(self, name: str) -> bool:
        return self.get_cds(name) is not None

    @classmethod
    def from_biopython(cls, record: SeqRecord) -> Self:
        if not record.id:
            raise MibigError("Record ID is required")

        ncbi_tax_id = None
        organism = None
        cdses = []
        for feature in record.features:
            if feature.type == "source":
                if "organism" in feature.qualifiers:
                    organism = feature.qualifiers["organism"][0]
                if "db_xref" in feature.qualifiers:
                    for db_xref in feature.qualifiers["db_xref"]:
                        if db_xref.startswith("taxon:"):
                            ncbi_tax_id = int(db_xref.split(":")[1])

            if feature.type != "CDS":
                continue

            locus_tag = feature.qualifiers.get("locus_tag", [None])[0]
            gene = feature.qualifiers.get("gene", [None])[0]
            protein_id = feature.qualifiers.get("protein_id", [None])[0]
            translation = feature.qualifiers.get("translation", [None])[0]

            cdses.append(CDS(locus_tag=locus_tag, gene=gene, protein_id=protein_id, translation=translation))

        return cls(id=record.id, cdses=cdses, seq_len=len(record.seq), ncbi_tax_id=ncbi_tax_id, organism=organism)


def load_records(filepath: str) -> list[Record]:
    return [Record.from_biopython(record) for record in seqio.parse(filepath)]
