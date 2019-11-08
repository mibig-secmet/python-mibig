class Saccharide:
    def __init__(self, raw):
        self.glycosyltransferases = [GlycosylTransferase(gt) for gt in raw.get("glycosyltransferases", [])] or []
        self.subclass = raw.get("subclass")  # str
        self.sugar_subclusters = raw.get("sugar_subclusters", [])  # list[str]

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

    @property
    def specificity_pretty(self):
        if self.specificity == "Unknown":
            return ""
        return self.specificity
