from collections import OrderedDict
from typing import List


class Thioesterase:
    def __init__(self, raw):
        self.gene = raw.get("gene")  # str
        self.thioesterase_type = raw.get("thioesterase_type")  # str
        assert self.thioesterase_type in {None, "Unknown", "Type II", "Type I"}


class NonCanonical:
    EVIDENCE = {"Sequence-based prediction", "Structure-based inference", "Activity assay"}

    def __init__(self, evidence: List[str],
                 iterated: bool = None, non_elongating: bool = None, skipped: bool = None):
        self.evidence = evidence
        assert evidence and not set(self.evidence).difference(self.EVIDENCE)
        self.iterated = iterated
        self.non_elongating = non_elongating
        self.skipped = skipped

    def to_json(self):
        result = OrderedDict()
        result["evidence"] = self.evidence
        if self.iterated is not None:
            result["iterated"] = self.iterated
        if self.non_elongating is not None:
            result["non_elongating"] = self.non_elongating
        if self.skipped is not None:
            result["skipped"] = self.skipped
        return result


class SpecificityBase:
    EVIDENCE = {"Sequence-based prediction", "Structure-based inference", "Feeding study", "Activity assay"}

    def __init__(self, substrates: List[str], evidence: List[str]):
        assert substrates and evidence
        assert not set(self.evidence).difference(self.EVIDENCE)


class ModuleBase:
    def __init__(self, module_number: str, gene_names: List[str], core_domains: List[str],
                 specificities: List[SpecificityBase] = None, modification_domains: List[str] = None,
                 non_canonical: NonCanonical = None, comments: str = ""):
        assert (module_number[0].isalpha() and module_number[1:].isnum()) or module_number.isnum()
        self.module_number = module_number
        self.gene_names = gene_names
        assert gene_names
        self.core_domains = core_domains
        assert core_domains
        self.specificities = specificities or []
        self.modification_domains = modification_domains or []
        self.non_canonical = non_canonical
        self.comments = comments

    def to_json(self):
        result = OrderedDict()
        result["module_number"] = self.module_number

        if self.gene_names:
            result["gene_names"] = self.gene_names

        result["core_domains"] = self.core_domains
        if self.modification_domains:
            result["modification_domains"] = self.modification_domains
        if self.specificities:
            result["specificities"] = [spec.to_json() for spec in self.specificities]
        if self.non_canonical:
            result["non_canonical"] = self.non_canonical.to_json()
        if self.comments:
            result["comment"] = self.comments

