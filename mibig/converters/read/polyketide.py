from .shared import NonCanonical, Thioesterase

class Polyketide:
    def __init__(self, raw):
        self.cyclases = raw.get("cyclases")  # list[str]
        self.cyclic = raw.get("cyclic")  # bool
        self.ketide_length = raw.get("ketide_length")  # int
        self.release_type = raw.get("release_type")  # list[str]
        self.starter_unit = raw.get("starter_unit")  # list[str]
        self.subclasses = raw.get("subclasses")  # list[str]
        self.synthases = [Synthase(syn) for syn in raw.get("synthases", [])] or []

    def __str__(self):
        if not self.subclasses:
            return "Polyketide"
        return "Polyketide ({})".format(", ".join(self.subclasses))


class Synthase:
    def __init__(self, raw):
        self.genes = raw["genes"]  # list[str]
        assert self.genes

        self.iterative = Iterative(raw["iterative"]) if "iterative" in raw else None
        self.modules = [PKSModule(mod) for mod in raw.get("modules", [])] or None
        self.pufa_modification_domains = raw.get("pufa_modification_domains")  # list[str]
        self.subclass = raw.get("subclass")  # list[str]  TODO: should be subclasses in out
        self.thioesterases = [Thioesterase(te) for te in raw.get("thioesterases", [])] or None
        self.trans_at = TransAT(raw.get("trans_at")) if "trans_at" in raw else None


class Iterative:
    EVIDENCE = {"Sequence-based prediction", "Structure-based inference", "Activity assay"}
    SUBTYPE = {"Partially reducing", "Non-reducing", "Highly reducing"}

    def __init__(self, raw):
        self.cyclization_type = raw["cyclization_type"]  # str
        self.subtype = raw["subtype"]  # str
        assert self.subtype in self.SUBTYPE

        self.evidence = raw.get("evidence")
        assert self.evidence is None or self.evidence in self.EVIDENCE
        self.genes = raw.get("genes")  # list str


class PKSModule:
    EVIDENCE = {"Sequence-based prediction", "Structure-based inference", "Feeding study", "Activity assay"}
    KR = {"Unknown", "Inactive", "L-OH", "D-OH"}

    def __init__(self, raw):
        self.at_specificities = raw.get("at_specificities")  # list[str]
        self.comments = raw.get("comments")  # str
        self.domains = raw.get("domains")  # list[str]
        self.evidence = raw.get("evidence")  # str
        assert self.evidence is None or self.evidence in self.EVIDENCE
        self.genes = raw.get("genes")  # list[str]
        assert self.genes is None or self.genes
        self.kr_stereochem = raw.get("kr_stereochem")
        assert self.kr_stereochem is None or self.kr_stereochem in self.KR
        self.module_number = raw.get("module_number")  # str
        assert self.module_number is None or self.module_number.isalnum()
        self.non_canonical = NonCanonical(raw.get("non_canonical")) if "non_canonical" in raw else None
        self.modification_domains = raw.get("pks_mod_doms")  # list[str]


class TransAT:
    def __init__(self, raw):
        self.genes = raw.get("genes")  # list[str]
        if self.genes is not None:
            assert self.genes
