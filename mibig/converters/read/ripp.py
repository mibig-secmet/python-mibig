class RiPP:
    def __init__(self, raw):
        self.cyclic = raw.get("cyclic")  # bool
        self.peptidases = raw.get("peptidases")  # list[str]
        self.precursor_genes = [PrecursorGene(pg) for pg in raw.get("precursor_genes", [])] or None
        self.subclass = raw.get("subclass") # str
        if "precursor_genes" in raw:
            assert self.precursor_genes


class PrecursorGene:
    def __init__(self, raw):
        self.gene_id = raw["gene_id"]  # str
        self.core_sequence = raw["core_sequence"]  # list[str]  # TODO: seems wrong

        self.cleavage_recognition_sites = raw.get("cleavage_recogn_site")  # list[str]
        self.crosslinks = [CrossLink(cl) for cl in raw.get("crosslinks", [])] or None
        self.follower_sequence = raw.get("follower_sequence")  # str
        self.leader_sequence = raw.get("leader_sequence")  # str
        self.recognition_motif = raw.get("recognition_motif")  # str


class CrossLink:
    def __init__(self, raw):
        self.type = raw["crosslink_type"]  # str
        assert self.type
        self.first_AA_position = raw.get("first_AA")  # int
        self.second_AA_position = raw.get("second_AA")  # int
