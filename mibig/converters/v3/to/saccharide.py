from collections import OrderedDict
from typing import List


class GlycosylTransferase:
    EVIDENCE = {"Sequence-based prediction", "Structure-based inference", "Knock-out construct", "Activity assay"}

    def __init__(self, evidence: List[str], gene_id: str, specificity: str):
        self.evidence = evidence
        assert evidence
        for piece in evidence:
            assert piece in self.EVIDENCE
        self.gene_id = gene_id
        self.specificity = specificity

    def to_json(self):
        result = OrderedDict()
        result["gene_id"] = self.gene_id
        result["specificity"] = self.specificity
        result["evidence"] = self.evidence
        return result


class Saccharide:
    def __init__(self, transferases: List[GlycosylTransferase] = None, subclass: str = None, sugar_subclusters: List[str] = None):
        self.glycosyl_transferases = transferases or []
        self.subclass = subclass or ""
        self.sugar_subclusters = sugar_subclusters or []
        if self.sugar_subclusters is not None:
            assert self.sugar_subclusters

    def to_json(self):
        result = OrderedDict()
        if self.subclass:
            result["subclass"] = self.subclass
        if self.glycosyl_transferases:
            result["glycosyltransferases"] = [gt.to_json() for gt in self.glycosyl_transferases]
        if self.sugar_subclusters:
            result["sugar_subclusters"] = self.sugar_subclusters
        return result
