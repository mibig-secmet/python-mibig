class Saccharide:
    def __init__(self, raw):
        self.glycosyl_transferases = [GlycosylTransferase(gt) for gt in raw.get("glycosyltransferases", [])] or None
        self.subclass = raw.get("subclass")  # str
        self.sugar_subclusters = raw.get("sugar_subclusters")  # list[str]
        if self.sugar_subclusters is not None:
            assert self.sugar_subclusters

    def __str__(self):
        if not self.subclass:
            return "Saccharide"
        return "Saccharide ({})".format(self.subclass)


class GlycosylTransferase:
    EVIDENCE = {"Sequence-based prediction", "Structure-based inference", "Knock-out construct", "Activity assay"}
    def __init__(self, raw):
        self.evidence = raw["evidence"]  # list[str]
        assert self.evidence is not None and not set(self.evidence).difference(self.EVIDENCE)
        self.gene_id = raw["gene_id"]  # str
        self.specificity = raw["specificity"]  # str
        
