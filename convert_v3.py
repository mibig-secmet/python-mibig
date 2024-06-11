#!/usr/bin/env python3
# convert from v3 MIBiG to v4 MIBiG schema

from argparse import ArgumentParser, FileType
from datetime import date
import sys

import orjson

from mibig.converters.shared.common import (
    ChangeLog,
    Citation,
    GeneId,
    Location,
    NovelGeneId,
    Release,
    ReleaseEntry,
    ReleaseVersion,
    Smiles,
    SubmitterID,
)
from mibig.converters.shared.mibig import MibigEntry
from mibig.converters.shared.mibig.biosynthesis import (
    Biosynthesis,
    Operon,
    OperonEvidence,
)
from mibig.converters.shared.mibig.biosynthesis.classes.base import (
    BiosynthesisClass,
    ExtraInfo as ExtraClassInfo,
    SynthesisType,
)
from mibig.converters.shared.mibig.biosynthesis.classes.nrps import NRPS
from mibig.converters.shared.mibig.biosynthesis.classes.other import Other
from mibig.converters.shared.mibig.biosynthesis.classes.pks import PKS
from mibig.converters.shared.mibig.biosynthesis.classes.ribosomal import (
    Crosslink,
    Precursor,
    Ribosomal,
)
from mibig.converters.shared.mibig.biosynthesis.classes.saccharide import (
    GTEvidence,
    Glycosyltransferase,
    Saccharide,
    Subcluster as SaccSubcluster,
)
from mibig.converters.shared.mibig.biosynthesis.classes.terpene import Terpene
from mibig.converters.shared.mibig.biosynthesis.common import ReleaseType
from mibig.converters.shared.mibig.biosynthesis.domains.acyltransferase import (
    ATSubstrate,
    Acyltransferase,
)
from mibig.converters.shared.mibig.biosynthesis.domains.adenylation import (
    Adenylation,
    AdenylationSubstrate,
    PROTEINOGENIC_SUBSTRATES,
)
from mibig.converters.shared.mibig.biosynthesis.domains.base import (
    Domain,
    DomainType,
)
from mibig.converters.shared.mibig.biosynthesis.domains.branching import Branching
from mibig.converters.shared.mibig.biosynthesis.domains.carrier import Carrier
from mibig.converters.shared.mibig.biosynthesis.domains.condensation import Condensation
from mibig.converters.shared.mibig.biosynthesis.domains.dehydratase import Dehydratase
from mibig.converters.shared.mibig.biosynthesis.domains.enoylreductase import (
    Enoylreductase,
)
from mibig.converters.shared.mibig.biosynthesis.domains.epimerase import Epimerase
from mibig.converters.shared.mibig.biosynthesis.domains.hydroxylase import Hydroxylase
from mibig.converters.shared.mibig.biosynthesis.domains.ketoreductase import (
    Ketoreductase,
)
from mibig.converters.shared.mibig.biosynthesis.domains.ketosynthase import Ketosynthase
from mibig.converters.shared.mibig.biosynthesis.domains.ligase import Ligase
from mibig.converters.shared.mibig.biosynthesis.domains.methyltransferase import (
    Methyltransferase,
)
from mibig.converters.shared.mibig.biosynthesis.domains.other import (
    Other as OtherDomain,
)
from mibig.converters.shared.mibig.biosynthesis.domains.oxidase import Oxidase
from mibig.converters.shared.mibig.biosynthesis.domains.product_template import (
    ProductTemplate,
)
from mibig.converters.shared.mibig.biosynthesis.domains.thioesterase import Thioesterase
from mibig.converters.shared.mibig.biosynthesis.domains.thioreductase import (
    Thioreductase,
)
from mibig.converters.shared.mibig.biosynthesis.modules.base import (
    Module,
    ModuleType,
    NcaEvidence,
    NonCanonicalActivity,
)
from mibig.converters.shared.mibig.biosynthesis.modules.nrps import NrpsTypeI
from mibig.converters.shared.mibig.biosynthesis.modules.pks import (
    PksModular,
    PksModularStarter,
    PksTransAt,
    PksTransAtStarter,
)
from mibig.converters.shared.mibig.common import (
    CompletenessLevel,
    Locus,
    LocusEvidence,
    QualityLevel,
    StatusLevel,
    SubstrateEvidence,
    Taxonomy,
)
from mibig.converters.shared.mibig.compound import Compound, CompoundRef
from mibig.converters.shared.mibig.genes import (
    Addition,
    Annotation,
    GeneLocation,
    Genes,
)
from mibig.converters.v3.read.nrp import NRPSGene, NRPSModule
from mibig.converters.v3.read.polyketide import PKSModule
from mibig.converters.v3.read.top import Everything


MIBIG_VERSION_TO_DATE = {
    "1.0": date(2015, 6, 12),
    "1.1": date(2015, 8, 17),
    "1.2": date(2015, 12, 24),
    "1.3": date(2016, 9, 3),
    "1.4": date(2018, 8, 6),
    "2.0": date(2019, 10, 16),
    "3.0": date(2022, 9, 15),
    "3.1": date(2022, 10, 7),
}


COMPLETENESS_MAPPING = {
    "complete": CompletenessLevel.COMPLETE,
    "incomplete": CompletenessLevel.PARTIAL,
    "Unknown": CompletenessLevel.UNKNOWN,
}


def main():
    parser = ArgumentParser(description="Convert MIBiG v3 JSON to MIBiG v4 JSON")
    parser.add_argument(
        "input",
        type=FileType("rb"),
        help="Input JSON file (MIBiG v3 format)",
    )
    parser.add_argument(
        "output",
        type=FileType("wb"),
        help="Output JSON file (MIBiG v4 format)",
    )
    args = parser.parse_args()

    v3_data = Everything(orjson.loads(args.input.read()))

    changelog = convert_changelog(v3_data)

    status = StatusLevel(v3_data.cluster.status)
    assert v3_data.cluster.loci
    completeness = COMPLETENESS_MAPPING[v3_data.cluster.loci.completeness]
    loci = convert_loci(v3_data)
    biosynthesis = convert_biosynthesis(v3_data)

    taxonomy = Taxonomy(v3_data.cluster.organism_name, int(v3_data.cluster.ncbi_tax_id))

    retirement_reasons = None
    if status == StatusLevel.RETIRED:
        retirement_reasons = v3_data.cluster.retirement_reasons

    compounds = convert_compounds(v3_data)
    genes = convert_genes(v3_data, biosynthesis)

    see_also = None
    if v3_data.cluster.see_also:
        see_also = []
        for see in v3_data.cluster.see_also:
            see_also.append(see)

    entry = MibigEntry(
        accession=v3_data.cluster.mibig_accession,
        version=len(changelog.releases) + 1,
        changelog=changelog,
        quality=QualityLevel.QUESTIONABLE,  # imported entries are questionable until proven otherwise
        status=status,
        completeness=completeness,
        loci=loci,
        biosynthesis=biosynthesis,
        compounds=compounds,
        taxonomy=taxonomy,
        genes=genes,
        retirement_reasons=retirement_reasons,
        see_also=see_also,
        comment=v3_data.comments,
    )
    args.output.write(orjson.dumps(entry.to_json()))


def convert_genes(v3_data: Everything, biosynthesis: Biosynthesis) -> Genes | None:
    to_add = []
    to_delete = []
    annotations = []
    quality = QualityLevel.QUESTIONABLE
    if not v3_data.cluster.genes:
        return None

    for extra_gene in v3_data.cluster.genes.extra_genes:
        gene_id = GeneId(extra_gene.id)
        exons: list[Location] = []
        assert extra_gene.location
        for exon in extra_gene.location.exons:
            exons.append(Location(exon.start, exon.end))
        location = GeneLocation(exons, extra_gene.location.strand)
        new_gene = Addition(
            id=gene_id,
            location=location,
            translation=extra_gene.translation,
            quality=quality,
        )
        to_add.append(new_gene)

    for v3_gene in v3_data.cluster.genes.annotations:
        gene_id = GeneId(v3_gene.id, quality=quality)
        name = None
        aliases = None
        if v3_gene.name:
            v3_name = v3_gene.name
            if "/" in v3_gene.name:
                aliases = []
                parts = v3_gene.name.split("/")
                v3_name = parts.pop(0)
                for alias in parts:
                    aliases.append(NovelGeneId(alias, quality=quality))

            name = NovelGeneId(v3_name)
        product = v3_gene.product
        domains = []
        for v3_domain in v3_gene.domains:
            loc = Location(v3_domain.location.begin, v3_domain.location.end)
            dt = DomainType(v3_domain.name.lower())
            if dt in (DomainType.ADENYLATION, DomainType.AMP_BINDING):
                substrates = []
                evidence = []
                for v3_substrate in v3_domain.substrates:
                    structure = None
                    proteinogenic = (
                        v3_substrate.name.lower() in PROTEINOGENIC_SUBSTRATES
                    )
                    if v3_substrate.structure:
                        structure = Smiles(v3_substrate.structure)
                    substrates.append(
                        AdenylationSubstrate(
                            name=v3_substrate.name,
                            proteinogenic=proteinogenic,
                            structure=structure,
                        )
                    )
                    for ev in v3_substrate.evidence:
                        if ev == "Sequence-based prediction":
                            # We don't do predictions for evidence anymore
                            continue
                        references = [
                            Citation(pub.category, pub.content)
                            for pub in v3_substrate.publications
                        ]
                        evidence.append(
                            SubstrateEvidence(
                                method=ev,
                                references=references,
                                quality=quality,
                            )
                        )
                extra_info = Adenylation(
                    substrates=substrates,
                    evidence=evidence,
                    precursor_biosynthesis=[],
                    quality=quality,
                )
            else:
                raise NotImplementedError(
                    f"Domain conversion for {v3_domain.name} not implemented"
                )
            domain = Domain(
                domain_type=dt,
                gene=gene_id,
                location=loc,
                extra_info=extra_info,
                quality=quality,
            )
            domains.append(domain)

        annotation = Annotation(
            id=gene_id,
            name=name,
            aliases=aliases,
            product=product,
            domains=domains,
            quality=quality,
        )
        annotations.append(annotation)

    for v3_operon in v3_data.cluster.genes.operons:
        genes = [GeneId(g) for g in v3_operon.genes]
        evidence = []
        for ev in v3_operon.evidence:
            if ev == "Sequence-based prediction":
                # We don't do predictions for evidence anymore
                continue
            evidence.append(OperonEvidence(ev, references=[], quality=quality))
        operon = Operon(genes=genes, evidence=evidence, quality=quality)
        biosynthesis.operons.append(operon)

    return Genes(
        to_add=to_add,
        to_delete=to_delete,
        annotations=annotations,
        quality=quality,
    )


def convert_compounds(v3_data: Everything) -> list[Compound]:
    compounds = []

    for v3_cmpd in v3_data.cluster.compounds:
        structure = None

        compound = Compound(
            name=v3_cmpd.compound,
            evidence=[],
            structure=structure,
            databases=[
                CompoundRef(ref.db, ref.reference) for ref in v3_cmpd.database_id
            ],
            mass=v3_cmpd.mol_mass,
            quality=QualityLevel.QUESTIONABLE,  # imported entries are questionable until proven otherwise
        )
        compounds.append(compound)

    return compounds


BIOSYN_CLASS_MAPPING: dict[str, SynthesisType] = {
    "NRP": SynthesisType.NRPS,
    "Polyketide": SynthesisType.PKS,
    "RiPP": SynthesisType.RIBOSOMAL,
    "Saccharide": SynthesisType.SACCHARIDE,
    "Terpene": SynthesisType.TERPENE,
    "Other": SynthesisType.OTHER,
}


def convert_biosynthesis(v3_data: Everything) -> Biosynthesis:
    quality = QualityLevel.QUESTIONABLE
    classes: list[BiosynthesisClass] = []
    modules: list[Module] = []

    other_subclass = None
    other_details = None

    for biosyn_class in v3_data.cluster.biosynthetic_class:
        class_name = BIOSYN_CLASS_MAPPING.get(biosyn_class)
        if class_name is None:
            if biosyn_class == "Alkaloid":
                # Alkaloids are not a biosynthetic class, switch to "other"
                class_name = SynthesisType.OTHER
                other_subclass = "other"
                other_details = "converted from 'Alkaloid'"

            else:
                raise ValueError(f"Unknown biosynthetic class: {biosyn_class}")

        if class_name == SynthesisType.NRPS:
            added_modules, extra_info = convert_nrps(v3_data, quality)
            modules.extend(added_modules)
        elif class_name == SynthesisType.PKS:
            added_modules, extra_info = convert_pks(v3_data, quality)
            modules.extend(added_modules)
        elif class_name == SynthesisType.RIBOSOMAL:
            extra_info = convert_ribosomal(v3_data, quality)
        elif class_name == SynthesisType.SACCHARIDE:
            extra_info = convert_saccharide(v3_data, quality)
        elif class_name == SynthesisType.TERPENE:
            extra_info = convert_terpene(v3_data, quality)
        elif class_name == SynthesisType.OTHER:
            extra_info = convert_other(v3_data, quality, other_subclass, other_details)
        else:
            raise NotImplementedError(
                f"Conversion of biosynthesis class {biosyn_class} not implemented"
            )

        classes.append(BiosynthesisClass(class_name, extra_info, quality=quality))

    return Biosynthesis(
        classes=classes, modules=modules, operons=[], paths=[], quality=quality
    )


def convert_other(
    v3_data: Everything,
    quality: QualityLevel,
    other_subclass: str | None,
    other_details: str | None,
) -> Other:
    v3 = v3_data.cluster.other
    if v3:
        if v3.subclass.lower() in ("unknown", "other"):
            return Other(
                "other", "converted from v3 without extra details", quality=quality
            )
        return Other(v3.subclass.lower(), quality=quality)

    if other_subclass:
        return Other(other_subclass, other_details, quality=quality)

    return Other("other", "converted from v3 without extra details", quality=quality)


def convert_saccharide(v3_data: Everything, quality: QualityLevel) -> Saccharide:
    glycosyltransferases: list[Glycosyltransferase] = []
    subclusters: list[SaccSubcluster] = []
    subclass: str | None = None
    v3 = v3_data.cluster.saccharide
    if v3:
        subclass = v3.subclass
        if v3.glycosyltransferases:
            for gt in v3.glycosyltransferases:
                evidence: list[GTEvidence] = []
                for ev in gt.evidence:
                    if ev == "Sequence-based prediction":
                        # We don't do predictions for evidence anymore
                        continue
                    evidence.append(GTEvidence(ev, references=[], quality=quality))
                gene_id = GeneId(gt.gene_id)
                specificity = Smiles(
                    "[To][Do]"
                )  # TODO: figure out how to convert specificity
                glycosyltransferase = Glycosyltransferase(
                    gene=gene_id, evidence=evidence, specificity=specificity
                )
                glycosyltransferases.append(glycosyltransferase)

        if v3.sugar_subclusters:
            for subcluster in v3.sugar_subclusters:
                genes: list[GeneId] = []
                for gene in subcluster:
                    genes.append(GeneId(gene))
                sacc_subcluster = SaccSubcluster(
                    genes=genes, references=[], quality=quality
                )
                subclusters.append(sacc_subcluster)

    return Saccharide(
        subclusters=subclusters,
        glycosyltransferases=glycosyltransferases,
        subclass=subclass,
    )


def convert_terpene(v3_data: Everything, quality: QualityLevel) -> Terpene:
    v3 = v3_data.cluster.terpene
    if not v3:
        return Terpene(
            subclass="Unknown", prenyltransferases=[], synthases=[], quality=quality
        )

    prenyltransferases = []
    for pt in v3.prenyltransferases:
        prenyltransferases.append(GeneId(pt))
    synthases = []
    for synthase in v3.synth_cycl:
        synthases.append(GeneId(synthase))

    return Terpene(
        subclass=v3.carbon_count_subclass,
        synthases=synthases,
        prenyltransferases=prenyltransferases,
        quality=quality,
    )


def convert_ribosomal(v3_data: Everything, quality: QualityLevel) -> Ribosomal:
    v3 = v3_data.cluster.ripp
    if not v3:
        subclass = "RiPP"
        ripp_type = None
        return Ribosomal(
            subclass=subclass, ripp_type=ripp_type, precursors=[], quality=quality
        )

    if v3.subclass in Ribosomal.VALID_RIPP_TYPES:
        subclass = "RiPP"
        ripp_type = v3.subclass
    else:
        subclass = "unmodified"
        ripp_type = None

    precursors = []
    for v3_pre in v3.precursor_genes:
        crosslinks = []
        for v3_cl in v3_pre.crosslinks:
            cl = Crosslink(
                v3_cl.first_AA_position, v3_cl.second_AA_position, v3_cl.type
            )
            crosslinks.append(cl)
        leader_cleavage_location = None
        if v3_pre.leader_sequence:
            leader_len = len(v3_pre.leader_sequence)
            leader_cleavage_location = Location(leader_len - 1, leader_len)
        follower_cleavage_location = None
        precursor = Precursor(
            gene=GeneId(v3_pre.gene_id),
            core_sequence=v3_pre.core_sequence,
            crosslinks=crosslinks,
            leader_cleavage_location=leader_cleavage_location,
            follower_clavage_location=follower_cleavage_location,
        )
        precursors.append(precursor)

    peptidases = []
    for peptidase in v3.peptidases:
        peptidases.append(GeneId(peptidase))

    return Ribosomal(
        subclass=subclass,
        precursors=precursors,
        ripp_type=ripp_type,
        peptidases=peptidases,
    )


def convert_pks(
    v3_data: Everything, quality: QualityLevel
) -> tuple[list[Module], ExtraClassInfo]:
    modules: list[Module] = []

    v3 = v3_data.cluster.polyketide
    subclass = "Unknown"
    if v3:
        for sc in v3.subclasses:
            if "type" in sc:
                subclass = sc
                break

        for synthase in v3.synthases:
            for sc in synthase.subclass:
                if "type" in sc.lower():
                    subclass = sc
                    break
            if subclass == "Modular type I":
                subclass = "Type I"
            for v3_module in synthase.modules:
                genes = [GeneId(gene) for gene in v3_module.genes]
                extra_domains: list[Domain] = []
                nc_activity = convert_nc_activity(v3_module, quality)
                at_domain = None
                if "Acyltransferase" in v3_module.domains:
                    specificities = []
                    for v3_spec in v3_module.at_specificities_pretty:
                        if v3_spec[0].isupper():
                            v3_spec = v3_spec[0].lower() + v3_spec[1:]
                        if v3_spec in ATSubstrate.VALID_NAMES:
                            spec = ATSubstrate(v3_spec, quality=quality)
                        else:
                            spec = ATSubstrate("other", v3_spec, quality=quality)
                        specificities.append(spec)
                    evidence = []
                    if v3_module.evidence:
                        ev = SubstrateEvidence(
                            method=v3_module.evidence, references=[], quality=quality
                        )
                        evidence.append(ev)
                    domain_type = DomainType.ACYLTRANSFERASE
                    domain_info = Acyltransferase(
                        substrates=specificities,
                        evidence=evidence,
                        quality=quality,
                    )
                    at_domain = Domain(
                        domain_type,
                        genes[0],
                        Location(-1, -1, quality=quality),
                        extra_info=domain_info,
                        quality=quality,
                    )

                ks_domain = None
                if "Ketosynthase" in v3_module.domains:
                    domain_type = DomainType.KETOSYNTHASE
                    domain_info = Ketosynthase()
                    ks_domain = Domain(
                        domain_type,
                        genes[0],
                        Location(-1, -1, quality=quality),
                        extra_info=domain_info,
                        quality=quality,
                    )

                carriers = []
                for domain in v3_module.domains:
                    if domain in (
                        "Thiolation (ACP/PCP)",
                        "ACP transacylase",
                        "Phosphopantetheinyl transferase",
                        "Beta-branching",
                    ):
                        branching = domain == "Beta-branching"
                        domain_type = DomainType.CARRIER
                        domain_info = Carrier(subtype="ACP", beta_branching=branching)
                        carrier = Domain(
                            domain_type,
                            genes[0],
                            Location(-1, -1, quality=quality),
                            extra_info=domain_info,
                            quality=quality,
                        )
                        carriers.append(carrier)

                v3_domains = v3_module.domains
                if v3_module.modification_domains:
                    v3_domains.extend(v3_module.modification_domains)

                for domain in v3_domains:
                    domain = domain.strip()
                    if domain in (
                        "Acyltransferase",
                        "Ketosynthase",
                        "Thiolation (ACP/PCP)",
                        "ACP transacylase",
                        "Phosphopantetheinyl transferase",
                        "Beta-branching",
                    ):
                        continue
                    elif domain == "Ketoreductase":
                        stereochem = None
                        if v3_module.kr_stereochem_pretty:
                            if v3_module.kr_stereochem_pretty == "L-OH":
                                stereochem = "A"
                            elif v3_module.kr_stereochem_pretty == "D-OH":
                                stereochem = "B"
                        domain_type = DomainType.KETOREDUCTASE
                        domain_info = Ketoreductase(
                            stereochemistry=stereochem, quality=quality
                        )
                    elif domain == "Dehydratase":
                        domain_type = DomainType.DEHYDRATASE
                        domain_info = Dehydratase()
                    elif domain == "Enoylreductase":
                        domain_type = DomainType.ENOYLREDUCTASE
                        domain_info = Enoylreductase()
                    elif domain == "Thioesterase":
                        domain_type = DomainType.THIOESTERASE
                        domain_info = Thioesterase()
                    elif domain == "Thiol reductase":
                        domain_type = DomainType.THIOREDUCTASE
                        domain_info = Thioreductase()
                    elif domain in ("Methylation", "Methyltransferase", "MT"):
                        domain_type = DomainType.METHYLTRANSFERASE
                        domain_info = Methyltransferase()
                    elif domain == "Product Template domain":
                        domain_type = DomainType.PRODUCT_TEMPLATE
                        domain_info = ProductTemplate()
                    elif domain == "CoA-ligase":
                        domain_type = DomainType.LIGASE
                        domain_info = Ligase(
                            substrates=[], evidence=[], quality=quality
                        )
                    elif domain in ("Michael branching", "B"):
                        domain_type = DomainType.BRANCHING
                        domain_info = Branching()
                    elif domain == "Epimerization":
                        domain_type = DomainType.EPIMERASE
                        domain_info = Epimerase()
                    elif domain in ("Oxidase", "Oxidation", "OXY"):
                        domain_type = DomainType.OXIDASE
                        domain_info = Oxidase()
                    elif domain == "Hydroxylation":
                        domain_type = DomainType.HYDROXYLASE
                        domain_info = Hydroxylase()
                    elif domain == "Sulfotransferase":
                        domain_type = DomainType.OTHER
                        domain_info = OtherDomain(subtype="Sulfotransferase")
                    elif domain == "Pyran synthase":
                        domain_type = DomainType.OTHER
                        domain_info = OtherDomain(subtype="Pyran synthase")
                    elif domain == "GNAT":
                        domain_type = DomainType.OTHER
                        domain_info = OtherDomain(subtype="GNAT")
                    elif domain in (
                        "Enoyl-CoA dehydratase",
                        "Crotonase / Enoyl-CoA dehydratase",
                    ):
                        domain_type = DomainType.OTHER
                        domain_info = OtherDomain(subtype="Enoyl-CoA dehydratase")
                    elif domain == "FkbH":
                        domain_type = DomainType.OTHER
                        domain_info = OtherDomain(subtype="FkbH")
                    elif domain == "AFSA":
                        domain_type = DomainType.OTHER
                        domain_info = OtherDomain(subtype="A-factor synthase A")
                    else:
                        raise ValueError(f"Unknown PKS domain type {domain!r}")
                    d = Domain(
                        domain_type,
                        genes[0],
                        Location(-1, -1, quality=quality),
                        extra_info=domain_info,
                        quality=quality,
                    )
                    extra_domains.append(d)
                if at_domain:
                    if ks_domain:
                        module_type = ModuleType.PKS_MODULAR
                        extra_info = PksModular(
                            subclass=subclass,
                            at_domain=at_domain,
                            ks_domain=ks_domain,
                            modification_domains=extra_domains,
                            carriers=carriers,
                            quality=quality,
                        )
                    else:
                        module_type = ModuleType.PKS_MODULAR_STARTER
                        extra_info = PksModularStarter(
                            subclass=subclass,
                            at_domain=at_domain,
                            modification_domains=extra_domains,
                            carriers=carriers,
                            quality=quality,
                        )
                else:
                    if ks_domain:
                        module_type = ModuleType.PKS_TRANS_AT
                        extra_info = PksTransAt(
                            subclass=subclass,
                            ks_domain=ks_domain,
                            modification_domains=extra_domains,
                            carriers=carriers,
                            quality=quality,
                        )
                    else:
                        module_type = ModuleType.PKS_TRANS_AT_STARTER
                        extra_info = PksTransAtStarter(
                            subclass=subclass,
                            modification_domains=extra_domains,
                            carriers=carriers,
                            quality=quality,
                        )
                module = Module(
                    module_type=module_type,
                    name=v3_module.module_number,
                    genes=genes,
                    active=True,
                    extra_info=extra_info,
                    integrated_monomers=[],
                    non_canonical_activity=nc_activity,
                    quality=quality,
                )
                modules.append(module)

    extra_info = PKS(subclass=subclass, cyclases=[], quality=quality)

    return modules, extra_info


def convert_nc_activity(
    v3_module: PKSModule | NRPSModule, quality: QualityLevel
) -> NonCanonicalActivity | None:
    if not v3_module.non_canonical:
        return

    evidence = []
    for ev in v3_module.non_canonical.evidence:
        if ev == "Sequence-based prediction":
            # We don't do predictions for evidence anymore
            continue
        evidence.append(NcaEvidence(method=ev, references=[], quality=quality))
    skipped = v3_module.non_canonical.skipped
    non_elongating = v3_module.non_canonical.non_elongating
    iterations = None
    if v3_module.non_canonical.iterated:
        iterations = -1
    return NonCanonicalActivity(
        evidence=evidence,
        skipped=skipped,
        non_elongating=non_elongating,
        iterations=iterations,
        quality=quality,
    )


def convert_nrps(
    v3_data: Everything, quality: QualityLevel
) -> tuple[list[Module], ExtraClassInfo]:
    thioesterases = []
    modules: list[Module] = []

    # Old style NRPSes are almost always Type I
    extra_info = NRPS(subclass="Type I", release_types=[], thioesterases=[])
    v3 = v3_data.cluster.nrp
    if not v3:
        return modules, extra_info

    if v3.release_type:
        release_types = []
        for rt in v3.release_type:
            if rt in ("Unknown", "Other"):
                continue
            release_types.append(ReleaseType(rt, [], quality=quality))

        if release_types:
            extra_info.release_types = release_types

    for v3_te in v3.thioesterases:
        subtype = None
        if v3_te.thioesterase_type != "Unknown":
            subtype = v3_te.thioesterase_type
        te = Thioesterase(subtype)
        te_domain = Domain(
            DomainType.THIOESTERASE,
            GeneId(v3_te.gene),
            Location(-1, -1, quality=quality),
            extra_info=te,
            quality=quality,
        )
        thioesterases.append(te_domain)
    extra_info.thioesterases = thioesterases

    if v3.nrps_genes:
        module_count = 1
        modules_by_id: dict[str, Module] = {}  # try to keep track of cross-CDS modules
        for nrps_gene in v3.nrps_genes:
            added_modules, module_count = convert_nrps_modules(
                nrps_gene, module_count, modules_by_id, quality
            )
            modules.extend(added_modules)

    return modules, extra_info


def convert_nrps_modules(
    nrps_gene: NRPSGene,
    module_count: int,
    modules_by_id: dict[str, Module],
    quality: QualityLevel,
) -> tuple[list[Module], int]:
    modules: list[Module] = []
    gene_id = GeneId(nrps_gene.gene_id)
    for v3_module in nrps_gene.modules:
        module_id = v3_module.module_number
        if not module_id:
            module_id = f"Unk{module_count:02d}"
            module_count += 1
        if module_id in modules_by_id:
            module = modules_by_id[module_id]
            module.genes.append(gene_id)
            continue

        if not v3_module.specificity:
            print(
                f"Warning: missing specificity for NRPS module {module_id}",
                file=sys.stderr,
            )
            continue

        nc_activity = convert_nc_activity(v3_module, quality)

        v3_spec = v3_module.specificity

        modification_domains: list[Domain] = []

        if v3_spec.epimerized:
            e = Epimerase(active=True)
            ed = Domain(
                DomainType.EPIMERASE,
                gene_id,
                Location(-1, -1, quality=quality),
                extra_info=e,
                quality=quality,
            )
            modification_domains.append(ed)

        carriers = []

        for v3_mod in v3_module.modification_domains:
            if v3_mod == "Methylation" or v3_mod.endswith("-methylation"):
                subtype = None
                if v3_mod.endswith("-methylation"):
                    subtype = v3_mod.split("-")[0]
                mi = Methyltransferase(subtype=subtype)
                mt = DomainType.METHYLTRANSFERASE
            elif v3_mod == "Epimerization":
                # we cover that separately
                continue
            elif v3_mod in ("Phosphopantetheinyl transferase", "Beta-branching"):
                branching = v3_mod == "Beta-branching"
                mt = DomainType.CARRIER
                mi = Carrier(subtype="PCP", beta_branching=branching)
                carriers.append(
                    Domain(
                        mt,
                        gene_id,
                        Location(-1, -1, quality=quality),
                        extra_info=mi,
                        quality=quality,
                    )
                )
                continue
            elif v3_mod in ("Hydroxylation", "beta-hydroxylation"):
                mt = DomainType.HYDROXYLASE
                mi = Hydroxylase()
            elif v3_mod == "CoA-ligase":
                mt = DomainType.LIGASE
                mi = Ligase(substrates=[], evidence=[], quality=quality)
            elif v3_mod == "Oxidation":
                mt = DomainType.OXIDASE
                mi = Oxidase()
            elif v3_mod == "Unknown":
                # yeah...
                continue
            else:
                raise ValueError(f"unsupported NRPS modification domain {v3_mod}")
            md = Domain(
                mt,
                gene_id,
                Location(-1, -1, quality=quality),
                extra_info=mi,
                quality=quality,
            )
            modification_domains.append(md)

        c_domain = None
        if v3_module.condensation_type:
            if v3_module.condensation_type == "Unknown":
                c = Condensation(None, [])
            else:
                c = Condensation(v3_module.condensation_type, [])
            c_domain = Domain(
                DomainType.CONDENSATION,
                gene_id,
                Location(-1, -1, quality=quality),
                extra_info=c,
                quality=quality,
            )

        substrates = []
        for v3_substrate in v3_spec.substrates:
            structure = None
            if v3_substrate.structure:
                structure = Smiles(v3_substrate.structure)

            substrates.append(
                AdenylationSubstrate(
                    v3_substrate.name, v3_substrate.proteinogenic, structure=structure
                )
            )

        evidence = []
        for v3_ev in v3_spec.evidence:
            evidence.append(
                SubstrateEvidence(method=v3_ev, references=[], quality=quality)
            )

        if len(evidence) == 1 and v3_spec.publications:
            evidence[0].references = [
                Citation(pub.category, pub.content) for pub in v3_spec.publications
            ]

        a_info = Adenylation(
            substrates=substrates,
            evidence=evidence,
            precursor_biosynthesis=[],
            quality=quality,
        )
        a_domain = Domain(
            DomainType.ADENYLATION,
            gene_id,
            Location(-1, -1, quality=quality),
            extra_info=a_info,
            quality=quality,
        )

        extra_info = NrpsTypeI(
            a_domain=a_domain,
            carriers=carriers,
            c_domain=c_domain,
            modification_domains=modification_domains,
            quality=quality,
        )
        module = Module(
            module_type=ModuleType.NRPS_TYPE1,
            name=module_id,
            genes=[gene_id],
            active=v3_module.active,
            extra_info=extra_info,
            integrated_monomers=[],
            non_canonical_activity=nc_activity,
            quality=quality,
        )
        modules.append(module)
        modules_by_id[module_id] = module

    return modules, module_count


def convert_loci(v3_data: Everything) -> list[Locus]:
    assert v3_data.cluster.loci
    begin = v3_data.cluster.loci.start or 0
    end = v3_data.cluster.loci.end or 0
    loc = Location(begin, end)
    evidence = []
    if v3_data.cluster.loci.evidence:
        evidence = [
            LocusEvidence(method=ev, references=[], quality=QualityLevel.QUESTIONABLE)
            for ev in v3_data.cluster.loci.evidence
        ]
    locus = Locus(
        accession=v3_data.cluster.loci.accession,
        location=loc,
        evidence=evidence,
    )
    return [locus]


REVIEW_MESSAGES = {
    "Changes reviewed and approved.",
    "Changes reviewed and approved",
    "Entry reviewed and approved.",
    "Reviewed changes and approved.",
}


def convert_changelog(v3_data: Everything) -> ChangeLog:
    mibig_user = SubmitterID("AAAAAAAAAAAAAAAAAAAAAAAA")

    releases: list[Release] = []

    for i, entry in enumerate(v3_data.changelog):
        if entry.mibig_version == "next":
            entry_date = None
            version = ReleaseVersion("next")
        else:
            entry_date = MIBIG_VERSION_TO_DATE[entry.mibig_version]
            version = ReleaseVersion(f"{i + 1}")

        release_entries: list[ReleaseEntry] = []
        if entry.timestamps:
            if len(entry.timestamps) != len(entry.comments) != len(entry.contributors):
                raise ValueError(
                    "Mismatch between number of comments, contributors and timestamps"
                )
            reviewers: list[SubmitterID] = []
            i = 0
            while i < len(entry.comments):
                if entry.comments[i] in REVIEW_MESSAGES:
                    reviewers.append(SubmitterID(entry.contributors[i]))
                    del entry.comments[i]
                    del entry.contributors[i]
                    continue
                i += 1
            for c, m, ts in zip(entry.contributors, entry.comments, entry.timestamps):
                ts = ts.split("T")[0]
                r_date = date.fromisoformat(ts)
                release_entry = ReleaseEntry(
                    date=r_date,
                    comment=m,
                    contributors=[SubmitterID(c)],
                    reviewers=reviewers,
                )
                release_entries.append(release_entry)

        elif len(entry.contributors) == len(entry.comments):
            assert entry_date is not None
            for c, m in zip(entry.contributors, entry.comments):
                release_entry = ReleaseEntry(
                    date=entry_date,
                    comment=m,
                    contributors=[SubmitterID(c)],
                    reviewers=[mibig_user],
                )
                release_entries.append(release_entry)
        elif len(entry.contributors) == 1:
            assert entry_date is not None
            for m in entry.comments:
                release_entry = ReleaseEntry(
                    date=entry_date,
                    comment=m,
                    contributors=[SubmitterID(entry.contributors[0])],
                    reviewers=[mibig_user],
                )
                release_entries.append(release_entry)
        elif entry.contributors[-1] == "AAAAAAAAAAAAAAAAAAAAAAAA":
            assert entry_date is not None
            j = 0
            while entry.contributors[j] != "AAAAAAAAAAAAAAAAAAAAAAAA":
                release_entry = ReleaseEntry(
                    date=entry_date,
                    comment=entry.comments[j],
                    contributors=[SubmitterID(entry.contributors[j])],
                    reviewers=[mibig_user],
                )
                release_entries.append(release_entry)
                j += 1
            for m in entry.comments[j:]:
                release_entry = ReleaseEntry(
                    date=entry_date,
                    comment=m,
                    contributors=[mibig_user],
                    reviewers=[mibig_user],
                )
                release_entries.append(release_entry)
        elif len(entry.comments) == 1:
            assert entry_date is not None
            release_entry = ReleaseEntry(
                date=entry_date,
                comment=entry.comments[0],
                contributors=[SubmitterID(c) for c in entry.contributors],
                reviewers=[mibig_user],
            )
            release_entries.append(release_entry)
        elif (
            entry.contributors[0] == "AAAAAAAAAAAAAAAAAAAAAAAA"
            and entry.contributors[-1] != "AAAAAAAAAAAAAAAAAAAAAAAA"
        ):
            assert entry_date is not None
            if set(entry.contributors[:-1]) == {"AAAAAAAAAAAAAAAAAAAAAAAA"}:
                for m in entry.comments[:-1]:
                    release_entry = ReleaseEntry(
                        date=entry_date,
                        comment=m,
                        contributors=[mibig_user],
                        reviewers=[mibig_user],
                    )
                    release_entries.append(release_entry)
                release_entry = ReleaseEntry(
                    date=entry_date,
                    comment=entry.comments[-1],
                    contributors=[SubmitterID(entry.contributors[-1])],
                    reviewers=[mibig_user],
                )
            else:
                raise ValueError("Mismatch between number of comments and contributors")
        elif len(entry.contributors) >= 3:
            assert entry_date is not None
            if (
                entry.contributors[0] != "AAAAAAAAAAAAAAAAAAAAAAAA"
                and entry.comments[0] == "Submitted"
                and entry.contributors[-1] != "AAAAAAAAAAAAAAAAAAAAAAAA"
                and set(entry.contributors[1:-1]) == {"AAAAAAAAAAAAAAAAAAAAAAAA"}
            ):
                release_entry = ReleaseEntry(
                    date=entry_date,
                    comment=entry.comments[0],
                    contributors=[SubmitterID(entry.contributors[0])],
                    reviewers=[mibig_user],
                )
                for m in entry.comments[:-1]:
                    release_entry = ReleaseEntry(
                        date=entry_date,
                        comment=m,
                        contributors=[mibig_user],
                        reviewers=[mibig_user],
                    )
                    release_entries.append(release_entry)
                release_entry = ReleaseEntry(
                    date=entry_date,
                    comment=entry.comments[-1],
                    contributors=[SubmitterID(entry.contributors[-1])],
                    reviewers=[mibig_user],
                )

        else:
            raise ValueError("Mismatch between number of comments and contributors")

        release = Release(
            version=version,
            date=entry_date,
            entries=release_entries,
        )
        releases.append(release)

    return ChangeLog(releases=releases)


if __name__ == "__main__":
    main()
