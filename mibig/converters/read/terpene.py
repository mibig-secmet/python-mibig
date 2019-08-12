class Terpene:
    def __init__(self, raw):
        self.carbon_count_subclass = raw.get("carbon_count_subclass")  # str
        self.prenyltransferases = raw.get("prenyltransferases")  # list[str]
        self.structural_subclass = raw.get("structural_subclass")  # str
        self.precursor = raw.get("terpene_precursor")  # str
        self.synth_cycl = raw.get("terpene_synth_cycl")  # list[str]
