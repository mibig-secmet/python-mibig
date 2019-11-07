from .alkaloid import Alkaloid
from .other import Other
from .polyketide import Polyketide
from .nrp import NRP
from .ripp import RiPP
from .saccharide import Saccharide


BIOSYNTHETIC_CLASSES = {"Alkaloid", "Polyketide", "RiPP", "NRP", "Saccharide", "Terpene", "Other"}


class Cluster:
    def __init__(self, raw):
        self.biosynthetic_class = [i for i in raw["biosyn_class"]]
        for item in self.biosynthetic_class:
            assert item in BIOSYNTHETIC_CLASSES
        assert self.biosynthetic_class
        self.mibig_accession = raw["mibig_accession"]  # str
        assert self.mibig_accession.startswith("BGC")
        assert len(self.mibig_accession) == 10
        assert int(self.mibig_accession[3:]) > 0
        self.compounds = [Compound(comp) for comp in raw["compounds"]]
        assert self.compounds
        self.publications = [Publication(pub) for pub in raw["publications"]]
        assert self.publications
        self.organism_name = raw["organism_name"]  # str
        self.ncbi_tax_id = raw["ncbi_tax_id"]  # str
        self.minimal = raw["minimal"]  # bool

        self.alkaloid = Alkaloid(raw.get("alkaloid")) if "alkaloid" in raw else None
        self.polyketide = Polyketide(raw.get("polyketide")) if "polyketide" in raw else None
        self.other = Other(raw.get("other")) if "other" in raw else None
        self.nrp = NRP(raw.get("nrp")) if "nrp" in raw else None
        self.loci = Loci(raw.get("loci")) if "loci" in raw else None
        self.genes = Genes(raw.get("genes")) if "genes" in raw else None
        self.ripp = RiPP(raw.get("ripp")) if "ripp" in raw else None
        self.saccharide = Saccharide(raw.get("saccharide")) if "saccharide" in raw else None
        self.terpene = Saccharide(raw.get("terpene")) if "terpene" in raw else None

        if not self.minimal:
            assert self.loci and self.loci.evidence


class Genes:
    def __init__(self, raw):
        self.annotations = [GeneAnnotation(ann) for ann in raw.get("annotations", [])] or []
        self.extra_genes = [ExtraGene(gene) for gene in raw.get("extra_genes", [])] or []
        self.operons = [Operon(op) for op in raw.get("operons", [])] or []


class GeneAnnotation:
    def __init__(self, raw):
        self.id = raw["id"]  # str

        self.comments = raw.get("comments")  # str
        self.functions = [GeneFunction(gf) for gf in raw.get("functions", [])] or []
        self.mutation_phenotype = raw.get("mut_pheno")  # str
        self.name = raw.get("name")  # str
        self.product = raw.get("product")  # str
        self.publications = raw.get("publications", [])  # list[str]
        self.tailoring = raw.get("tailoring", [])  # list[str]

    def to_json(self):
        return {
            "id": self.id,
            "comments": self.comments,
            "functions": [gf.to_json() for gf in self.functions],
            "mut_pheno": self.mutation_phenotype,
            "name": self.name,
            "product": self.product,
            "publications": self.publications,
            "tailoring": self.tailoring,
        }


class GeneFunction:
    EVIDENCE = {"Sequence-based prediction", "Other in vivo study", "Heterologous expression", "Knock-out", "Activity assay"}

    def __init__(self, raw):
        self.category = raw["category"]  # str
        self.evidence = raw["evidence"]  # list[str]
        assert not set(self.evidence).difference(self.EVIDENCE)

    def to_json(self):
        return {"category": self.category, "evidence": self.evidence}


class ExtraGene:
    def __init__(self, raw):
        self.id = raw["id"]  # str

        self.location = Location(raw.get("location")) if "location" in raw else None
        self.translation = raw.get("translation")

    def to_json(self):
        return {
            "location": self.location.to_json() if self.location else None,
            "translation": self.translation,
        }


class Location:
    def __init__(self, raw):
        self.exons = [Exon(exon) for exon in raw["exons"]]
        assert self.exons
        self.strand = raw["strand"]
        assert self.strand in [-1, 1]

    def to_json(self):
        return {
            "exons": [exon.to_json() for exon in self.exons],
            "strand": self.strand,
        }


class Exon:
    def __init__(self, raw):
        self.start = raw["start"]
        self.end = raw["end"]

    def to_json(self):
        return {"start": self.start, "end": self.end}


class Operon:
    EVIDENCE = {"Sequence-based prediction", "RACE", "ChIPseq", "RNAseq"}

    def __init__(self, raw):
        self.genes = raw["genes"]  # list[str]
        assert self.genes
        self.evidence = raw["evidence"]  # list[str]
        assert not set(self.evidence).difference(self.EVIDENCE)


class Loci:
    EVIDENCE = {"Sequence-based prediction", "Gene expression correlated with compound production", "Knock-out studies", "Enzymatic assays", "Heterologous expression"}

    def __init__(self, raw):
        self.accession = raw["accession"]  # str
        self.completeness = raw["completeness"]  # bool
        self.start = raw.get("start_coord")  # int
        assert self.start is None or self.start >= 1
        self.end = raw.get("end_coord")  # int
        assert self.end is None or self.end >= 2
        self.mixs_compliant = raw.get("mixs_compliant")  # bool
        self.evidence = raw.get("evidence")  # list[str]
        assert self.evidence is None or not set(self.evidence).difference(self.EVIDENCE)


class Publication:
    def __init__(self, raw):
        assert raw.split(":")[0] in {"pubmed", "doi", "patent", "url"}
        assert not raw.endswith(":")
        self.text = raw


class Compound:
    def __init__(self, raw):
        self.chem_acts = raw.get("chem_acts")                                     # list[str]
        self.chem_moieties = [Moiety(mo) for mo in raw.get("chem_moieties", [])] or []
        self.chem_struct = raw.get("chem_struct")                                 # str
        self.chem_synonyms = raw.get("chem_synonyms", [])                         # list[str]
        self.chem_targets = [ChemTarget(target) for target in raw.get("chem_targets", [])] or []
        self.compound = raw["compound"]                                           # str
        self.database_id = [DatabaseID(dbid) for dbid in raw.get("database_id", [])] or []
        self.evidence = raw.get("evidence", [])                                   # list[str]
        self.mass_spec_ion_type = raw.get("mass_spec_ion_type")                   # str
        self.mol_mass = raw.get("mol_mass")                                       # number
        self.molecular_formula = raw.get("molecular_formula")                    # str


class ChemTarget:
    def __init__(self, raw):
        self.publications = raw.get("publications")  # list[str]
        self.target = raw.get("target")              # str


class Moiety:
    def __init__(self, raw):
        self.moiety = raw["moiety"]          # str
        self.subcluster = raw.get("subcluster", [])  # list[str]


class DatabaseID:
    def __init__(self, raw):
        db, ref = raw.split(":")
        assert db in {"pubchem", "chebi", "chembl", "chemspider", "npatlas"}
        int(ref)
        self.text = raw                                                            # str
