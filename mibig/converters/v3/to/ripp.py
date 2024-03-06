from collections import OrderedDict
from typing import List


class CrossLink:
    def __init__(self, crosslink_type: str,
                 first_AA_position: int = None, second_AA_position: int = None):
        self.type = crosslink_type
        assert self.type
        self.first_AA_position = first_AA_position
        self.second_AA_position = second_AA_position

    def to_json(self):
        result = OrderedDict()
        result["type"] = self.type
        if self.first_AA_position:
            result["first_AA"] = self.first_AA_position
        if self.second_AA_position:
            result["second_AA"] = self.second_AA_position
        return result


class Precursor:
    def __init__(self, gene_id: str, cores: List[str],
                 cleavage_recognition_sites: List[str] = None, crosslinks: List[CrossLink] = None, follower: str = None, leader: str = None, recognition_motif: str = None):
        self.gene_id = gene_id
        self.cores = cores  # TODO why multiple?
        assert cores

        self.cleavage_recognition_sites = cleavage_recognition_sites
        self.crosslinks = crosslinks
        self.follower_sequence = follower
        self.leader_sequence = leader
        self.recognition_motif = recognition_motif

    def to_json(self):
        result = OrderedDict()
        result["gene_id"] = self.gene_id
        result["core_sequence"] = self.cores

        if self.cleavage_recognition_sites:
            result["cleavage_recogn_sites"] = self.cleavage_recognition_sites
        if self.crosslinks:
            result["crosslinks"] = [link.to_json() for link in self.crosslinks]
        if self.follower_sequence:
            result["follower_sequence"] = self.follower_sequence
        if self.leader_sequence:
            result["leader_sequence"] = self.leader_sequence
        if self.recognition_motif:
            result["recognition_motif"] = self.recognition_motif

        return result


class RiPP:
    def __init__(self, cyclic: bool = None, peptidases: List[str] = None, precursor_genes: List[Precursor] = None):
        self.cyclic = cyclic
        assert peptidases is None or peptidases
        self.peptidases = peptidases or []
        assert precursor_genes is None or precursor_genes
        self.precursor_genes = precursor_genes or []

    def to_json(self):
        result = OrderedDict()
        if self.cyclic:
            result["cyclic"] = self.cyclic
        if self.peptidases:
            result["peptidases"] = self.peptidases
        if self.precursor_genes:
            result["precuror_genes"] = [pre.to_json() for pre in self.precursor_genes]
        return result
