from .shared import Thioesterase, NonCanonical, SpecifityBase


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



    def __init__(self,module_number: str, gene_names: List[str], core_domains: List[str],
                 specificities: List[SpecificityBase] = None, modification_domains: List[str] = None,
                 non_canonical: NonCanonical = None, comments: str = ""):

class NRPSModule:
    CONDENSATIONS = {"Dual", "Starter", "LCL", "Unknown", "DCL", "Ester bond-forming", "Heterocyclization"}

    def __init__(self, module_number: str, specificity: Specificity,
                 condensation_subtype: str = None, core_domains: List[str] = None, modification_domains: List[str] = None,
                 epimerized: bool = None, comment: str = "", non_canonical: NonCanonical = None):
        super().__init__(module_number, gene_names, specificities=[specificity], core_domains=core_domains,
                         modification_domains=modification_domains, non_canonical=non_canonical, comments=comment)
        self.condensation_subtype = condensation_subtype
        assert self.condensation_type is None or self.condensation_type in self.CONDENSATIONS
        self.epimerized = epimerized

    def to_json(self):
        result = super().to_json()
        if self.condensation


class Specificity(SpecificityBase):
    LOADED = {"Alanine", "Arginine", "Glutamate", "Serine", "Tryptophan", "Methionine", "Threonine", "Glycine", "Isoleucine", "Proline",
              "Glutamine", "Tyrosine", "Phenylalanine", "Cysteine", "Histidine", "Leucine", "Lysine", "Valine", "Asparagine", "Aspartate"}

    def __init__(self, substrates: List[str], evidence: List[str], subcluster: List[str] = None):
        super().__init__(substrates, evidence)
        self.subcluster = subcluster or []

    def to_json(self):
        result = super().to_json()
        if self.subcluster:
            result["aa_subcluster"] = self.subcluster
        return result
