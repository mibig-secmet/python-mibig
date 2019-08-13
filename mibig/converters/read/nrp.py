from .shared import Thioesterase, NonCanonical


class NRP:
    def __init__(self, raw):
        self.cyclic = raw.get("cyclic")  # str
        self.lipid_moiety = raw.get("lipid_moiety")  # str
        self.nrps_genes = [NRPSGene(gene) for gene in raw.get("nrps_genes", [])] or None
        self.release_type = raw.get("release_type")  # str
        self.subclass = raw.get("subclass")  # str
        self.thioesterases = [Thioesterase(te) for te in raw.get("thioesterases", [])] or None


class NRPSGene:
    def __init__(self, raw):
        self.gene_id = raw.get("gene_id")  # str
        self.modules = [NRPSModule(mod) for mod in raw.get("modules", [])] or None


class NRPSModule:
    CONDENSATIONS = {"Dual", "Starter", "LCL", "Unknown", "DCL", "Ester bond-forming", "Heterocyclization"}

    def __init__(self, raw):
        self.specificity = Specificity(raw.get("a_substr_spec")) if "a_substr_spec" in raw else None
        self.active = raw.get("active")  # bool
        self.condensation_type = raw.get("c_dom_subtype")
        assert self.condensation_type is None or self.condensation_type in self.CONDENSATIONS
        self.comments = raw.get("comments")  # str
        self.modification_domains = raw.get("modification_domains")
        self.module_number = raw.get("module_number")
        self.non_canonical = NonCanonical(raw.get("non_canonical")) if "non_canonical" in raw else None


class Specificity:
    EVIDENCE = {"Sequence-based prediction", "Structure-based inference", "Feeding study", "Activity assay"}
    LOADED = {"Alanine", "Arginine", "Glutamate", "Serine", "Tryptophan", "Methionine", "Threonine", "Glycine", "Isoleucine", "Proline",
              "Glutamine", "Tyrosine", "Phenylalanine", "Cysteine", "Histidine", "Leucine", "Lysine", "Valine", "Asparagine", "Aspartate"}

    def __init__(self, raw):
        self.subcluster = raw.get("aa_subcluster")  # list[str]
        self.epimerized = raw.get("epimerized")  # bool
        self.evidence = raw.get("evidence")  # list[str]
        assert self.evidence is None or not set(self.evidence).difference(self.EVIDENCE)
        self.non_proteinogenic = raw.get("nonproteinogenic")  # list[str]
        self.proteinogenic = raw.get("proteinogenic")  # list[str]
        assert self.proteinogenic is None or not set(self.proteinogenic).difference(self.LOADED)
