from typing import List

from .shared import Thioesterase, NonCanonical, Publication


class NRP:
    def __init__(self, raw):
        self.cyclic = raw.get("cyclic")  # str  # should be bool?
        self.lipid_moiety = raw.get("lipid_moiety")  # str
        self.nrps_genes = [NRPSGene(gene) for gene in raw.get("nrps_genes", [])] or []
        self.release_type = raw.get("release_type")  # str
        self.subclass = raw.get("subclass")  # str
        self.thioesterases = [Thioesterase(te) for te in raw.get("thioesterases", [])] or []

    def __str__(self):
        if not self.subclass:
            return "NRP"
        return "NRP ({})".format(self.subclass)


class NRPSGene:
    def __init__(self, raw):
        self.gene_id = raw.get("gene_id")  # str
        self.modules = [NRPSModule(mod) for mod in raw.get("modules", [])] or []


class NRPSModule:
    CONDENSATIONS = {"Dual", "Starter", "LCL", "Unknown",
                     "DCL", "Ester bond-forming", "Heterocyclization"}

    def __init__(self, raw):
        self.specificity = Specificity(raw.get("a_substr_spec")) if "a_substr_spec" in raw else None
        self.active = raw.get("active")  # bool
        self.condensation_type = raw.get("c_dom_subtype")
        assert self.condensation_type is None or self.condensation_type in self.CONDENSATIONS
        self.comments = raw.get("comments")  # str
        self.modification_domains = raw.get("modification_domains", [])
        self.module_number = raw.get("module_number")
        self.non_canonical = NonCanonical(
            raw.get("non_canonical")) if "non_canonical" in raw else None


SUBSTRATE_EVIDENCE = {
    "Activity assay",
    "ACVS assay",
    "ATP-PPi exchange assay",
    "Feeding study",
    "Heterologous expression",
    "Homology",
    "In-vitro experiments",
    "Knock-out studies",
    "Mass spectrometry",
    "Radio labelling",
    "Sequence-based prediction",
    "Steady-state kinetics",
    "Structure-based inference",
    "X-ray crystallography"
}


class Specificity:
    def __init__(self, raw):
        self.subcluster = raw.get("aa_subcluster", [])  # list[str]
        self.epimerized = raw.get("epimerized")  # bool
        self.evidence = raw.get("evidence", [])  # list[str]
        assert self.evidence is None or not set(self.evidence).difference(SUBSTRATE_EVIDENCE)
        self.publications = [Publication(pub) for pub in raw.get("publications", [])] or []
        self.substrates = [NRPSSubstrate(sub) for sub in raw.get("substrates", [])] or []

    def __str__(self):
        return " / ".join([sub.name for sub in self.substrates])


class NRPSSubstrate:
    LOADED = {"Alanine", "Arginine", "Asparagine", "Aspartic acid", "Cysteine", "Glutamic acid",
              "Glutamine", "Glycine", "Histidine", "Isoleucine", "Leucine", "Lysine", "Methionine",
              "Phenylalanine", "Proline", "Serine", "Threonine", "Tryptophan", "Tyrosine", "Valine"}

    def __init__(self, raw):
        self.name: str = raw.get("name")
        self.proteinogenic: bool = raw.get("proteinogenic")
        self.structure: str = raw.get("structure")
        if self.proteinogenic:
            assert self.name in self.LOADED, f"{self.name} is no proteinogenic amino acid"
        else:
            assert self.name not in self.LOADED, f"{self.name} should be a proteinogenic amino acid"


class IntegratedMonomer:
    def __init__(self, raw):
        self.evidence: List[str] = raw.get("evidence", [])
        assert self.evidence is None or not set(self.evidence).difference(SUBSTRATE_EVIDENCE)
        self.name: str = raw.get("name")
        self.publications: List[Publication] = [Publication(pub)
                                                for pub in raw.get("publications", [])] or []
        self.structure: str = raw.get("structure")
