class Thioesterase:
    def __init__(self, raw):
        self.gene = raw.get("gene")  # str
        self.thioesterase_type = raw.get("thioesterase_type")  # str
        assert self.thioesterase_type in {None, "Unknown", "Type II", "Type I"}


class NonCanonical:
    EVIDENCE = {"Sequence-based prediction", "Structure-based inference", "Activity assay"}

    def __init__(self, raw):
        self.evidence = raw.get("evidence", [])
        assert self.evidence == [] or not set(self.evidence).difference(self.EVIDENCE)
        self.iterated = raw.get("iterated")  # bool
        self.non_elongating = raw.get("non_elongating")  # bool
        self.skipped = raw.get("skipped")  # bool


class Publication:
    def __init__(self, raw):
        assert not raw.endswith(":")
        category, content = raw.split(":", 1)
        assert category in {"pubmed", "doi", "patent", "url"}
        self.category = category
        self.content = content
