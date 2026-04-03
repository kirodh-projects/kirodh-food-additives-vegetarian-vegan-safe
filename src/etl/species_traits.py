"""Heuristic trait scoring for species.

Physical traits: mobility, warm-bloodedness, size.
Guna traits (Vedic): sattva (purity), rajas (passion), tamas (ignorance).

Each score is a probability from 0.0 to 1.0 assigned based on taxonomic
classification (kingdom > phylum > class > order), using the most specific
match available.

Scores represent *typical* values for the taxonomic group, not individual
organisms.  They are statistical heuristics, not measurements.

The three Gunas are scored so that sattva + rajas + tamas ≈ 1.0 for each
entry, reflecting the Vedic principle that all beings are composed of these
three qualities in varying proportions:
  - Sattva (purity): harmony, gentleness, nourishment, light, awareness
  - Rajas (passion): activity, desire, predation, competition, restlessness
  - Tamas (ignorance): inertia, darkness, decay, parasitism, unconsciousness
"""

import logging
from src.db.species_connection import get_species_connection, list_species_db_files

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════
#  PHYSICAL TRAITS
# ═══════════════════════════════════════════════════════════════════════

# ── Mobility (0 = sessile, 1 = highly mobile) ──────────────────────────

MOBILITY_BY_ORDER: dict[str, float] = {
    "Perciformes": 0.75, "Cypriniformes": 0.70, "Siluriformes": 0.65,
    "Characiformes": 0.70, "Cyprinodontiformes": 0.60, "Scorpaeniformes": 0.60,
    "Anguilliformes": 0.70, "Tetraodontiformes": 0.55, "Pleuronectiformes": 0.45,
    "Clupeiformes": 0.80, "Gadiformes": 0.70, "Salmoniformes": 0.85,
    "Beloniformes": 0.75, "Syngnathiformes": 0.30, "Lophiiformes": 0.25,
    "Myctophiformes": 0.65, "Osteoglossiformes": 0.60, "Ophidiiformes": 0.50,
    "Rajiformes": 0.55, "Carcharhiniformes": 0.85, "Lamniformes": 0.90,
    "Squaliformes": 0.70,
    "Sessilia": 0.01, "Pedunculata": 0.01,
}

MOBILITY_BY_CLASS: dict[str, float] = {
    "Mammalia": 0.85, "Aves": 0.95,
    "Amphibia": 0.65, "Squamata": 0.60, "Testudines": 0.25,
    "Crocodylia": 0.45, "Sphenodontia": 0.40,
    "Elasmobranchii": 0.80, "Holocephali": 0.60,
    "Petromyzonti": 0.50, "Dipneusti": 0.35, "Coelacanthi": 0.40,
    "Myxini": 0.40, "Leptocardii": 0.30,
    "Ascidiacea": 0.03, "Thaliacea": 0.25,
    "Insecta": 0.75, "Arachnida": 0.55, "Malacostraca": 0.60,
    "Copepoda": 0.45, "Diplopoda": 0.35, "Chilopoda": 0.50,
    "Collembola": 0.45, "Ostracoda": 0.30, "Trilobita": 0.40,
    "Branchiopoda": 0.40, "Merostomata": 0.35, "Pycnogonida": 0.25,
    "Maxillopoda": 0.30, "Remipedia": 0.45, "Cephalocarida": 0.30,
    "Pauropoda": 0.30, "Symphyla": 0.35,
    "Gastropoda": 0.20, "Bivalvia": 0.05, "Cephalopoda": 0.80,
    "Scaphopoda": 0.05, "Polyplacophora": 0.10, "Monoplacophora": 0.05,
    "Polychaeta": 0.30, "Clitellata": 0.25,
    "Chromadorea": 0.20, "Enoplea": 0.20,
    "Anthozoa": 0.02, "Hydrozoa": 0.15, "Scyphozoa": 0.30, "Cubozoa": 0.35,
    "Demospongiae": 0.01, "Calcarea": 0.01, "Hexactinellida": 0.01,
    "Echinoidea": 0.15, "Asteroidea": 0.15, "Holothuroidea": 0.10,
    "Ophiuroidea": 0.20, "Crinoidea": 0.05,
    "Trematoda": 0.25, "Cestoda": 0.05, "Turbellaria": 0.30,
    "Gymnolaemata": 0.01, "Stenolaemata": 0.01, "Phylactolaemata": 0.01,
    "Rhynchonellata": 0.02, "Lingulata": 0.02, "Craniata": 0.01,
    "Eurotatoria": 0.30, "Bdelloidea": 0.25,
    "Agaricomycetes": 0.0, "Dothideomycetes": 0.0, "Lecanoromycetes": 0.0,
    "Sordariomycetes": 0.0, "Leotiomycetes": 0.0, "Eurotiomycetes": 0.0,
    "Pezizomycetes": 0.0, "Pucciniomycetes": 0.0, "Ustilaginomycetes": 0.0,
    "Tremellomycetes": 0.0, "Dacrymycetes": 0.0, "Exobasidiomycetes": 0.0,
    "Magnoliopsida": 0.0, "Liliopsida": 0.0, "Polypodiopsida": 0.0,
    "Pinopsida": 0.0, "Bryopsida": 0.0, "Lycopodiopsida": 0.0,
    "Jungermanniopsida": 0.0, "Marchantiopsida": 0.0, "Gnetopsida": 0.0,
    "Cycadopsida": 0.0, "Anthocerotopsida": 0.0, "Sphagnopsida": 0.0,
    "Bacillariophyceae": 0.10, "Phaeophyceae": 0.0,
    "Chrysophyceae": 0.15, "Dinophyceae": 0.30,
    "Globothalamea": 0.10, "Tubothalamea": 0.05,
    "Oligohymenophorea": 0.50, "Spirotrichea": 0.50,
    "Litostomatea": 0.45, "Lobosa": 0.30,
}

MOBILITY_BY_PHYLUM: dict[str, float] = {
    "Chordata": 0.70, "Arthropoda": 0.55, "Mollusca": 0.25,
    "Annelida": 0.28, "Cnidaria": 0.10, "Nematoda": 0.20,
    "Platyhelminthes": 0.20, "Porifera": 0.01, "Echinodermata": 0.15,
    "Bryozoa": 0.01, "Brachiopoda": 0.02, "Ctenophora": 0.35,
    "Rotifera": 0.28, "Tardigrada": 0.20, "Hemichordata": 0.10,
    "Chaetognatha": 0.40, "Nemertea": 0.25, "Sipuncula": 0.10,
    "Acanthocephala": 0.05, "Onychophora": 0.30,
    "Tracheophyta": 0.0, "Bryophyta": 0.0, "Marchantiophyta": 0.0,
    "Rhodophyta": 0.0, "Chlorophyta": 0.05, "Charophyta": 0.0,
    "Anthocerotophyta": 0.0,
    "Ascomycota": 0.0, "Basidiomycota": 0.0, "Zygomycota": 0.0,
    "Glomeromycota": 0.0, "Chytridiomycota": 0.10,
    "Ochrophyta": 0.05, "Foraminifera": 0.08, "Ciliophora": 0.45,
    "Myzozoa": 0.30, "Haptophyta": 0.15,
    "Proteobacteria": 0.30, "Firmicutes": 0.20, "Actinobacteria": 0.10,
    "Cyanobacteria": 0.10, "Bacteroidetes": 0.15,
    "Euryarchaeota": 0.15, "Crenarchaeota": 0.10,
}

MOBILITY_BY_KINGDOM: dict[str, float] = {
    "Animalia": 0.45, "Plantae": 0.0, "Fungi": 0.0,
    "Chromista": 0.08, "Bacteria": 0.20, "Archaea": 0.12,
    "Protozoa": 0.40, "Viruses": 0.0, "incertae sedis": 0.10,
}

# ── Warm-bloodedness / endothermy (0 = ectotherm, 1 = full endotherm) ──

WARM_BLOOD_BY_ORDER: dict[str, float] = {
    "Lamniformes": 0.25, "Scombriformes": 0.15,
    "Testudines": 0.10,
    "Hymenoptera": 0.08, "Lepidoptera": 0.05, "Coleoptera": 0.03,
}

WARM_BLOOD_BY_CLASS: dict[str, float] = {
    "Mammalia": 0.95, "Aves": 0.95,
    "Elasmobranchii": 0.08, "Cephalopoda": 0.05,
    "Insecta": 0.03, "Squamata": 0.02,
}

WARM_BLOOD_BY_PHYLUM: dict[str, float] = {"Chordata": 0.05}

WARM_BLOOD_BY_KINGDOM: dict[str, float] = {
    "Animalia": 0.02, "Plantae": 0.0, "Fungi": 0.0,
    "Chromista": 0.0, "Bacteria": 0.0, "Archaea": 0.0,
    "Protozoa": 0.0, "Viruses": 0.0, "incertae sedis": 0.0,
}

# ── Body size (0 = microscopic, 1 = largest known organisms) ───────────

SIZE_BY_ORDER: dict[str, float] = {
    "Cetacea": 0.85, "Proboscidea": 0.82, "Perissodactyla": 0.72,
    "Artiodactyla": 0.68, "Carnivora": 0.60, "Sirenia": 0.70,
    "Rodentia": 0.30, "Chiroptera": 0.25, "Eulipotyphla": 0.22,
    "Lagomorpha": 0.30, "Primates": 0.48,
    "Crocodylia": 0.60,
    "Struthioniformes": 0.50, "Casuariiformes": 0.48,
    "Lamniformes": 0.65, "Orectolobiformes": 0.60,
    "Acari": 0.06,
}

SIZE_BY_CLASS: dict[str, float] = {
    "Mammalia": 0.50, "Aves": 0.35,
    "Amphibia": 0.22, "Squamata": 0.28, "Testudines": 0.40,
    "Crocodylia": 0.60, "Sphenodontia": 0.32,
    "Elasmobranchii": 0.50, "Holocephali": 0.40,
    "Petromyzonti": 0.30, "Dipneusti": 0.38, "Coelacanthi": 0.45,
    "Myxini": 0.28, "Leptocardii": 0.15,
    "Ascidiacea": 0.15, "Thaliacea": 0.12,
    "Insecta": 0.12, "Arachnida": 0.10, "Malacostraca": 0.20,
    "Copepoda": 0.06, "Diplopoda": 0.14, "Chilopoda": 0.14,
    "Collembola": 0.06, "Ostracoda": 0.05, "Trilobita": 0.15,
    "Branchiopoda": 0.06, "Merostomata": 0.25, "Pycnogonida": 0.10,
    "Maxillopoda": 0.06, "Pauropoda": 0.04, "Symphyla": 0.05,
    "Gastropoda": 0.14, "Bivalvia": 0.16, "Cephalopoda": 0.35,
    "Scaphopoda": 0.10, "Polyplacophora": 0.12, "Monoplacophora": 0.08,
    "Polychaeta": 0.14, "Clitellata": 0.14,
    "Chromadorea": 0.06, "Enoplea": 0.06,
    "Anthozoa": 0.15, "Hydrozoa": 0.08, "Scyphozoa": 0.25, "Cubozoa": 0.18,
    "Demospongiae": 0.18, "Calcarea": 0.10, "Hexactinellida": 0.20,
    "Echinoidea": 0.16, "Asteroidea": 0.20, "Holothuroidea": 0.22,
    "Ophiuroidea": 0.14, "Crinoidea": 0.18,
    "Trematoda": 0.06, "Cestoda": 0.12, "Turbellaria": 0.06,
    "Gymnolaemata": 0.04, "Stenolaemata": 0.04, "Phylactolaemata": 0.05,
    "Rhynchonellata": 0.10, "Lingulata": 0.08, "Craniata": 0.06,
    "Eurotatoria": 0.04, "Bdelloidea": 0.03,
    "Agaricomycetes": 0.14, "Dothideomycetes": 0.06, "Lecanoromycetes": 0.08,
    "Sordariomycetes": 0.06, "Leotiomycetes": 0.06, "Eurotiomycetes": 0.05,
    "Pezizomycetes": 0.08, "Pucciniomycetes": 0.04, "Ustilaginomycetes": 0.04,
    "Tremellomycetes": 0.06, "Dacrymycetes": 0.06, "Exobasidiomycetes": 0.04,
    "Magnoliopsida": 0.38, "Liliopsida": 0.30, "Polypodiopsida": 0.25,
    "Pinopsida": 0.65, "Bryopsida": 0.05, "Lycopodiopsida": 0.15,
    "Jungermanniopsida": 0.04, "Marchantiopsida": 0.04, "Gnetopsida": 0.30,
    "Cycadopsida": 0.45, "Anthocerotopsida": 0.04, "Sphagnopsida": 0.05,
    "Bacillariophyceae": 0.04, "Phaeophyceae": 0.30,
    "Chrysophyceae": 0.03, "Dinophyceae": 0.03,
    "Globothalamea": 0.04, "Tubothalamea": 0.04,
    "Oligohymenophorea": 0.04, "Spirotrichea": 0.04,
    "Litostomatea": 0.04, "Lobosa": 0.05,
}

SIZE_BY_PHYLUM: dict[str, float] = {
    "Chordata": 0.40, "Arthropoda": 0.12, "Mollusca": 0.16,
    "Annelida": 0.14, "Cnidaria": 0.14, "Nematoda": 0.06,
    "Platyhelminthes": 0.06, "Porifera": 0.16, "Echinodermata": 0.18,
    "Bryozoa": 0.04, "Brachiopoda": 0.08, "Ctenophora": 0.12,
    "Rotifera": 0.04, "Tardigrada": 0.04, "Hemichordata": 0.12,
    "Chaetognatha": 0.10, "Nemertea": 0.14, "Sipuncula": 0.10,
    "Acanthocephala": 0.06, "Onychophora": 0.12,
    "Tracheophyta": 0.38, "Bryophyta": 0.05, "Marchantiophyta": 0.04,
    "Rhodophyta": 0.15, "Chlorophyta": 0.08, "Charophyta": 0.10,
    "Anthocerotophyta": 0.04,
    "Ascomycota": 0.06, "Basidiomycota": 0.12, "Zygomycota": 0.04,
    "Glomeromycota": 0.04, "Chytridiomycota": 0.03,
    "Ochrophyta": 0.10, "Foraminifera": 0.04, "Ciliophora": 0.04,
    "Myzozoa": 0.03, "Haptophyta": 0.03,
    "Proteobacteria": 0.02, "Firmicutes": 0.02, "Actinobacteria": 0.02,
    "Cyanobacteria": 0.03, "Bacteroidetes": 0.02,
    "Euryarchaeota": 0.02, "Crenarchaeota": 0.02,
}

SIZE_BY_KINGDOM: dict[str, float] = {
    "Animalia": 0.22, "Plantae": 0.30, "Fungi": 0.10,
    "Chromista": 0.06, "Bacteria": 0.02, "Archaea": 0.02,
    "Protozoa": 0.04, "Viruses": 0.01, "incertae sedis": 0.10,
}


# ═══════════════════════════════════════════════════════════════════════
#  GUNA TRAITS  (sattva + rajas + tamas ≈ 1.0)
# ═══════════════════════════════════════════════════════════════════════
#
# Sattva (purity):  harmony, gentleness, nourishment, awareness, light
# Rajas  (passion): activity, desire, predation, competition, dynamism
# Tamas  (ignorance): inertia, darkness, decay, parasitism, unconsciousness
#
# Tuples are (sattva, rajas, tamas).

_GunaTuple = tuple[float, float, float]

# ── Order-level Gunas ──────────────────────────────────────────────────

GUNA_BY_ORDER: dict[str, _GunaTuple] = {
    # Herbivorous mammals — sattvic (gentle, nourishing)
    "Artiodactyla":     (0.60, 0.22, 0.18),   # cows, deer, antelope
    "Perissodactyla":   (0.52, 0.33, 0.15),   # horses, rhinos
    "Proboscidea":      (0.65, 0.18, 0.17),   # elephants — wise, gentle giants
    "Lagomorpha":       (0.50, 0.30, 0.20),   # rabbits
    "Sirenia":          (0.58, 0.12, 0.30),   # manatees — peaceful, slow
    "Cetacea":          (0.55, 0.28, 0.17),   # whales, dolphins — intelligent, graceful
    "Primates":         (0.42, 0.40, 0.18),   # complex — social, intelligent, competitive
    # Predatory mammals — rajasic
    "Carnivora":        (0.15, 0.68, 0.17),   # lions, wolves, bears
    "Chiroptera":       (0.18, 0.37, 0.45),   # bats — nocturnal, darkness
    "Rodentia":         (0.22, 0.48, 0.30),   # rats, mice — restless, adaptive
    "Eulipotyphla":     (0.20, 0.35, 0.45),   # shrews, moles — underground
    # Birds
    "Passeriformes":    (0.55, 0.30, 0.15),   # songbirds — sattvic, sky, melody
    "Psittaciformes":   (0.50, 0.35, 0.15),   # parrots — intelligent, colourful
    "Columbiformes":    (0.62, 0.22, 0.16),   # doves — peace, purity
    "Accipitriformes":  (0.12, 0.72, 0.16),   # eagles, hawks — fierce, rajasic
    "Falconiformes":    (0.12, 0.73, 0.15),   # falcons
    "Strigiformes":     (0.20, 0.40, 0.40),   # owls — nocturnal, wisdom mixed with darkness
    "Cathartiformes":   (0.08, 0.30, 0.62),   # vultures — scavengers, death
    "Galliformes":      (0.45, 0.35, 0.20),   # chickens, pheasants — domestic, nourishing
    "Anseriformes":     (0.48, 0.30, 0.22),   # ducks, geese, swans
    "Struthioniformes": (0.40, 0.35, 0.25),   # ostriches
    "Pelecaniformes":   (0.38, 0.40, 0.22),   # pelicans, herons
    # Reptiles
    "Crocodylia":       (0.05, 0.52, 0.43),   # crocodiles — ancient, predatory, lurking
    # Fish
    "Perciformes":      (0.22, 0.50, 0.28),   # perch — active fish
    "Cypriniformes":    (0.35, 0.35, 0.30),   # carp, goldfish — some kept as auspicious
    "Salmoniformes":    (0.38, 0.45, 0.17),   # salmon — determined, life-giving migration
    "Lamniformes":      (0.05, 0.75, 0.20),   # great white sharks — apex predators
    "Carcharhiniformes":(0.05, 0.70, 0.25),   # requiem sharks
    "Siluriformes":     (0.18, 0.35, 0.47),   # catfish — bottom-dwelling
    "Anguilliformes":   (0.12, 0.38, 0.50),   # eels — serpentine, darkness
    "Pleuronectiformes":(0.15, 0.25, 0.60),   # flatfish — bottom, camouflage
    # Beneficial insects
    "Hymenoptera":      (0.48, 0.40, 0.12),   # bees, ants — industrious, nourishing (honey)
    "Lepidoptera":      (0.52, 0.30, 0.18),   # butterflies — beauty, transformation
    # Other insects
    "Diptera":          (0.08, 0.37, 0.55),   # flies — decay, disease
    "Blattodea":        (0.05, 0.32, 0.63),   # cockroaches — filth, indestructible
    "Coleoptera":       (0.15, 0.40, 0.45),   # beetles — dung, darkness, some beauty
    "Hemiptera":        (0.10, 0.42, 0.48),   # bugs — parasitic, pest
    "Orthoptera":       (0.25, 0.45, 0.30),   # grasshoppers, crickets — active, noisy
    "Odonata":          (0.38, 0.48, 0.14),   # dragonflies — swift, light-loving
}

# ── Class-level Gunas ──────────────────────────────────────────────────

GUNA_BY_CLASS: dict[str, _GunaTuple] = {
    # Mammals — generally rajasic (driven, desiring, social)
    "Mammalia":         (0.30, 0.45, 0.25),
    # Birds — sattvic tendency (sky, freedom, song, light)
    "Aves":             (0.45, 0.35, 0.20),
    # Reptiles — tamasic tendency (cold, lurking, ancient)
    "Squamata":         (0.10, 0.35, 0.55),   # snakes, lizards — serpents = tamas in Vedic
    "Testudines":       (0.40, 0.10, 0.50),   # turtles — patience, but inertia
    "Crocodylia":       (0.05, 0.52, 0.43),
    "Sphenodontia":     (0.15, 0.20, 0.65),   # tuatara — ancient relics
    # Amphibians
    "Amphibia":         (0.18, 0.30, 0.52),   # damp, transitional, twilight
    # Fish (sharks)
    "Elasmobranchii":   (0.08, 0.65, 0.27),   # sharks, rays — predatory
    "Holocephali":      (0.12, 0.38, 0.50),   # chimaeras — deep, dark
    "Petromyzonti":     (0.05, 0.30, 0.65),   # lampreys — parasitic
    "Dipneusti":        (0.20, 0.25, 0.55),   # lungfish — mud, dormancy
    "Coelacanthi":      (0.25, 0.20, 0.55),   # coelacanth — deep, ancient
    "Myxini":           (0.03, 0.20, 0.77),   # hagfish — slime, scavenging, darkness
    "Leptocardii":      (0.20, 0.20, 0.60),   # lancelets — primitive
    # Tunicates
    "Ascidiacea":       (0.15, 0.05, 0.80),   # sea squirts — sessile, filter, inert
    "Thaliacea":        (0.18, 0.15, 0.67),   # salps — drifting
    # Arthropods
    "Insecta":          (0.18, 0.55, 0.27),   # insects — ceaseless rajasic activity
    "Arachnida":        (0.08, 0.40, 0.52),   # spiders — dark, venomous, patient traps
    "Malacostraca":     (0.20, 0.45, 0.35),   # crabs, shrimp — scavenging, active
    "Copepoda":         (0.15, 0.40, 0.45),   # tiny, drifting, consumed
    "Diplopoda":        (0.12, 0.20, 0.68),   # millipedes — soil, decay, darkness
    "Chilopoda":        (0.08, 0.50, 0.42),   # centipedes — venomous, predatory
    "Collembola":       (0.20, 0.30, 0.50),   # springtails — soil
    "Ostracoda":        (0.12, 0.28, 0.60),   # seed shrimp
    "Trilobita":        (0.15, 0.30, 0.55),   # extinct — ancient seas
    "Merostomata":      (0.18, 0.30, 0.52),   # horseshoe crabs — ancient
    # Mollusks
    "Gastropoda":       (0.18, 0.15, 0.67),   # snails, slugs — slow, earth, inertia
    "Bivalvia":         (0.22, 0.05, 0.73),   # clams, oysters — sessile, filtering, inert
    "Cephalopoda":      (0.25, 0.55, 0.20),   # octopus, squid — intelligent, active, hunters
    "Scaphopoda":       (0.10, 0.08, 0.82),   # tusk shells — buried, inert
    "Polyplacophora":   (0.12, 0.10, 0.78),   # chitons — rock-clinging
    # Annelids
    "Polychaeta":       (0.15, 0.30, 0.55),   # marine worms
    "Clitellata":       (0.28, 0.18, 0.54),   # earthworms — soil fertility (some sattva)
    # Nematodes
    "Chromadorea":      (0.05, 0.30, 0.65),   # roundworms — parasitic, soil
    "Enoplea":          (0.05, 0.28, 0.67),
    # Cnidaria
    "Anthozoa":         (0.30, 0.05, 0.65),   # corals — build reefs (creation) but sessile
    "Hydrozoa":         (0.10, 0.25, 0.65),
    "Scyphozoa":        (0.10, 0.22, 0.68),   # jellyfish — drifting, stinging
    "Cubozoa":          (0.05, 0.35, 0.60),   # box jellyfish — deadly venom
    # Sponges — most tamasic animals (no nerves, no movement, no awareness)
    "Demospongiae":     (0.12, 0.03, 0.85),
    "Calcarea":         (0.12, 0.03, 0.85),
    "Hexactinellida":   (0.12, 0.03, 0.85),
    # Echinoderms
    "Echinoidea":       (0.15, 0.15, 0.70),   # sea urchins — spiny, slow
    "Asteroidea":       (0.18, 0.22, 0.60),   # starfish — slow predators
    "Holothuroidea":    (0.15, 0.08, 0.77),   # sea cucumbers — bottom, inert
    "Ophiuroidea":      (0.12, 0.25, 0.63),   # brittle stars
    "Crinoidea":        (0.18, 0.05, 0.77),   # sea lilies — sessile
    # Flatworms — parasitic = tamasic
    "Trematoda":        (0.03, 0.30, 0.67),   # flukes — parasites
    "Cestoda":          (0.02, 0.18, 0.80),   # tapeworms — internal parasites, darkness
    "Turbellaria":      (0.12, 0.30, 0.58),   # planarians — free-living
    # Bryozoa
    "Gymnolaemata":     (0.12, 0.05, 0.83),   # colonial, sessile
    "Stenolaemata":     (0.10, 0.05, 0.85),
    "Phylactolaemata":  (0.12, 0.05, 0.83),
    # Brachiopods
    "Rhynchonellata":   (0.12, 0.05, 0.83),
    "Lingulata":        (0.15, 0.05, 0.80),
    # Rotifers
    "Eurotatoria":      (0.12, 0.35, 0.53),
    "Bdelloidea":       (0.15, 0.25, 0.60),
    # ── Fungi ──
    # Decomposers of the dead — tamasic (darkness, decay, dissolution)
    "Agaricomycetes":   (0.18, 0.07, 0.75),   # mushrooms — some medicinal/sacred → bit of sattva
    "Dothideomycetes":  (0.05, 0.15, 0.80),   # plant pathogens
    "Lecanoromycetes":  (0.22, 0.05, 0.73),   # lichens — enduring, patient
    "Sordariomycetes":  (0.05, 0.15, 0.80),   # many plant/insect pathogens
    "Leotiomycetes":    (0.08, 0.12, 0.80),
    "Eurotiomycetes":   (0.12, 0.15, 0.73),   # Aspergillus, Penicillium — some healing (sattva)
    "Pezizomycetes":    (0.12, 0.08, 0.80),   # cup fungi, truffles
    "Pucciniomycetes":  (0.03, 0.20, 0.77),   # rust fungi — plant parasites
    "Ustilaginomycetes":(0.03, 0.18, 0.79),   # smut fungi
    "Tremellomycetes":  (0.10, 0.08, 0.82),
    "Dacrymycetes":     (0.10, 0.08, 0.82),
    "Exobasidiomycetes":(0.05, 0.15, 0.80),
    # ── Plants ──
    # Plants are generally sattvic (nourishment, oxygen, shade, beauty)
    "Magnoliopsida":    (0.68, 0.15, 0.17),   # flowering plants — fruits, flowers, medicine
    "Liliopsida":       (0.62, 0.15, 0.23),   # grasses, lilies, orchids, grains
    "Polypodiopsida":   (0.48, 0.10, 0.42),   # ferns — shade, damp forests
    "Pinopsida":        (0.58, 0.12, 0.30),   # conifers — evergreen, enduring
    "Bryopsida":        (0.38, 0.05, 0.57),   # mosses — damp, ground, shade
    "Lycopodiopsida":   (0.42, 0.08, 0.50),   # clubmosses
    "Jungermanniopsida":(0.35, 0.05, 0.60),   # liverworts
    "Marchantiopsida":  (0.35, 0.05, 0.60),
    "Gnetopsida":       (0.45, 0.15, 0.40),
    "Cycadopsida":      (0.50, 0.10, 0.40),   # cycads — ancient, enduring
    "Anthocerotopsida": (0.35, 0.05, 0.60),   # hornworts
    "Sphagnopsida":     (0.35, 0.05, 0.60),   # peat moss — bogs, decay
    # ── Chromista ──
    "Bacillariophyceae":(0.30, 0.15, 0.55),   # diatoms — photosynthetic (sattva) but tiny
    "Phaeophyceae":     (0.40, 0.10, 0.50),   # brown algae, kelp — ocean forests
    "Chrysophyceae":    (0.25, 0.20, 0.55),
    "Dinophyceae":      (0.12, 0.30, 0.58),   # dinoflagellates — some toxic (red tides)
    "Globothalamea":    (0.12, 0.15, 0.73),   # forams
    "Tubothalamea":     (0.12, 0.10, 0.78),
    # ── Protozoa ──
    "Oligohymenophorea":(0.10, 0.45, 0.45),   # ciliates — active hunters
    "Spirotrichea":     (0.10, 0.45, 0.45),
    "Litostomatea":     (0.08, 0.48, 0.44),
    "Lobosa":           (0.08, 0.35, 0.57),   # amoebae — formless, engulfing
}

# ── Phylum-level Gunas ─────────────────────────────────────────────────

GUNA_BY_PHYLUM: dict[str, _GunaTuple] = {
    "Chordata":         (0.28, 0.42, 0.30),
    "Arthropoda":       (0.15, 0.48, 0.37),
    "Mollusca":         (0.18, 0.18, 0.64),
    "Annelida":         (0.20, 0.22, 0.58),
    "Cnidaria":         (0.15, 0.15, 0.70),
    "Nematoda":         (0.05, 0.28, 0.67),
    "Platyhelminthes":  (0.05, 0.25, 0.70),
    "Porifera":         (0.12, 0.03, 0.85),
    "Echinodermata":    (0.15, 0.15, 0.70),
    "Bryozoa":          (0.12, 0.05, 0.83),
    "Brachiopoda":      (0.12, 0.05, 0.83),
    "Ctenophora":       (0.15, 0.25, 0.60),
    "Rotifera":         (0.12, 0.30, 0.58),
    "Tardigrada":       (0.20, 0.15, 0.65),   # resilient, enduring
    "Hemichordata":     (0.15, 0.15, 0.70),
    "Chaetognatha":     (0.08, 0.45, 0.47),   # arrow worms — predatory
    "Nemertea":         (0.10, 0.30, 0.60),
    "Sipuncula":        (0.12, 0.10, 0.78),
    "Acanthocephala":   (0.03, 0.25, 0.72),   # thorny-headed worms — parasites
    "Onychophora":      (0.15, 0.30, 0.55),   # velvet worms
    # Plants
    "Tracheophyta":     (0.62, 0.15, 0.23),
    "Bryophyta":        (0.38, 0.05, 0.57),
    "Marchantiophyta":  (0.35, 0.05, 0.60),
    "Rhodophyta":       (0.38, 0.10, 0.52),   # red algae
    "Chlorophyta":      (0.40, 0.15, 0.45),   # green algae
    "Charophyta":       (0.38, 0.10, 0.52),
    "Anthocerotophyta": (0.35, 0.05, 0.60),
    # Fungi
    "Ascomycota":       (0.08, 0.15, 0.77),
    "Basidiomycota":    (0.15, 0.10, 0.75),
    "Zygomycota":       (0.05, 0.12, 0.83),
    "Glomeromycota":    (0.20, 0.08, 0.72),   # mycorrhizal — symbiotic with plants (sattva)
    "Chytridiomycota":  (0.05, 0.18, 0.77),
    # Chromista
    "Ochrophyta":       (0.30, 0.12, 0.58),
    "Foraminifera":     (0.12, 0.12, 0.76),
    "Ciliophora":       (0.10, 0.45, 0.45),
    "Myzozoa":          (0.08, 0.30, 0.62),   # includes malaria parasites
    "Haptophyta":       (0.25, 0.15, 0.60),
    # Bacteria
    "Proteobacteria":   (0.18, 0.32, 0.50),
    "Firmicutes":       (0.20, 0.25, 0.55),
    "Actinobacteria":   (0.25, 0.20, 0.55),   # soil bacteria, antibiotic production
    "Cyanobacteria":    (0.45, 0.15, 0.40),   # photosynthetic — created Earth's O₂
    "Bacteroidetes":    (0.15, 0.25, 0.60),
    # Archaea
    "Euryarchaeota":    (0.12, 0.18, 0.70),
    "Crenarchaeota":    (0.10, 0.15, 0.75),
}

# ── Kingdom-level Gunas ────────────────────────────────────────────────

GUNA_BY_KINGDOM: dict[str, _GunaTuple] = {
    "Animalia":         (0.22, 0.43, 0.35),
    "Plantae":          (0.65, 0.12, 0.23),   # plants are the most sattvic kingdom
    "Fungi":            (0.12, 0.12, 0.76),   # decomposers — tamasic
    "Chromista":        (0.25, 0.18, 0.57),
    "Bacteria":         (0.18, 0.28, 0.54),
    "Archaea":          (0.12, 0.15, 0.73),   # ancient, extremophile, darkness
    "Protozoa":         (0.10, 0.42, 0.48),
    "Viruses":          (0.03, 0.35, 0.62),   # parasitic, destructive, no consciousness
    "incertae sedis":   (0.15, 0.25, 0.60),
}


# ═══════════════════════════════════════════════════════════════════════
#  RESOLUTION HELPERS
# ═══════════════════════════════════════════════════════════════════════

def _resolve(
    kingdom: str, phylum: str, class_name: str, order_name: str,
    by_order: dict[str, float],
    by_class: dict[str, float],
    by_phylum: dict[str, float],
    by_kingdom: dict[str, float],
    default: float = 0.5,
) -> float:
    """Return the most-specific matching score."""
    if order_name and order_name in by_order:
        return by_order[order_name]
    if class_name and class_name in by_class:
        return by_class[class_name]
    if phylum and phylum in by_phylum:
        return by_phylum[phylum]
    if kingdom and kingdom in by_kingdom:
        return by_kingdom[kingdom]
    return default


def _resolve_guna(
    kingdom: str, phylum: str, class_name: str, order_name: str,
    by_order: dict[str, _GunaTuple],
    by_class: dict[str, _GunaTuple],
    by_phylum: dict[str, _GunaTuple],
    by_kingdom: dict[str, _GunaTuple],
    default: _GunaTuple = (0.33, 0.34, 0.33),
) -> _GunaTuple:
    """Return the most-specific matching guna tuple."""
    if order_name and order_name in by_order:
        return by_order[order_name]
    if class_name and class_name in by_class:
        return by_class[class_name]
    if phylum and phylum in by_phylum:
        return by_phylum[phylum]
    if kingdom and kingdom in by_kingdom:
        return by_kingdom[kingdom]
    return default


def compute_mobility(kingdom: str, phylum: str, class_name: str, order_name: str) -> float:
    return _resolve(kingdom, phylum, class_name, order_name,
                    MOBILITY_BY_ORDER, MOBILITY_BY_CLASS,
                    MOBILITY_BY_PHYLUM, MOBILITY_BY_KINGDOM, 0.25)


def compute_warm_blood(kingdom: str, phylum: str, class_name: str, order_name: str) -> float:
    return _resolve(kingdom, phylum, class_name, order_name,
                    WARM_BLOOD_BY_ORDER, WARM_BLOOD_BY_CLASS,
                    WARM_BLOOD_BY_PHYLUM, WARM_BLOOD_BY_KINGDOM, 0.0)


def compute_size(kingdom: str, phylum: str, class_name: str, order_name: str) -> float:
    return _resolve(kingdom, phylum, class_name, order_name,
                    SIZE_BY_ORDER, SIZE_BY_CLASS,
                    SIZE_BY_PHYLUM, SIZE_BY_KINGDOM, 0.10)


def compute_gunas(kingdom: str, phylum: str, class_name: str, order_name: str) -> _GunaTuple:
    return _resolve_guna(kingdom, phylum, class_name, order_name,
                         GUNA_BY_ORDER, GUNA_BY_CLASS,
                         GUNA_BY_PHYLUM, GUNA_BY_KINGDOM, (0.33, 0.34, 0.33))


# ═══════════════════════════════════════════════════════════════════════
#  SQL GENERATION
# ═══════════════════════════════════════════════════════════════════════

def _build_case_sql(
    by_order: dict[str, float],
    by_class: dict[str, float],
    by_phylum: dict[str, float],
    by_kingdom: dict[str, float],
    default: float,
) -> str:
    """Build a CASE expression for a single float column."""
    parts = []
    for name, val in by_order.items():
        parts.append(f"WHEN order_name = '{name}' THEN {val}")
    for name, val in by_class.items():
        parts.append(f"WHEN class_name = '{name}' THEN {val}")
    for name, val in by_phylum.items():
        parts.append(f"WHEN phylum = '{name}' THEN {val}")
    for name, val in by_kingdom.items():
        parts.append(f"WHEN kingdom = '{name}' THEN {val}")
    case_body = "\n        ".join(parts)
    return f"""CASE
        {case_body}
        ELSE {default}
    END"""


def _build_guna_case_sql(
    by_order: dict[str, _GunaTuple],
    by_class: dict[str, _GunaTuple],
    by_phylum: dict[str, _GunaTuple],
    by_kingdom: dict[str, _GunaTuple],
    default: _GunaTuple,
    idx: int,
) -> str:
    """Build a CASE expression for one component (0=sattva, 1=rajas, 2=tamas)."""
    parts = []
    for name, vals in by_order.items():
        parts.append(f"WHEN order_name = '{name}' THEN {vals[idx]}")
    for name, vals in by_class.items():
        parts.append(f"WHEN class_name = '{name}' THEN {vals[idx]}")
    for name, vals in by_phylum.items():
        parts.append(f"WHEN phylum = '{name}' THEN {vals[idx]}")
    for name, vals in by_kingdom.items():
        parts.append(f"WHEN kingdom = '{name}' THEN {vals[idx]}")
    case_body = "\n        ".join(parts)
    return f"""CASE
        {case_body}
        ELSE {default[idx]}
    END"""


def build_trait_update_sql() -> str:
    """Build a single UPDATE statement that sets all six trait columns."""
    mobility_case = _build_case_sql(
        MOBILITY_BY_ORDER, MOBILITY_BY_CLASS,
        MOBILITY_BY_PHYLUM, MOBILITY_BY_KINGDOM, 0.25,
    )
    warm_blood_case = _build_case_sql(
        WARM_BLOOD_BY_ORDER, WARM_BLOOD_BY_CLASS,
        WARM_BLOOD_BY_PHYLUM, WARM_BLOOD_BY_KINGDOM, 0.0,
    )
    size_case = _build_case_sql(
        SIZE_BY_ORDER, SIZE_BY_CLASS,
        SIZE_BY_PHYLUM, SIZE_BY_KINGDOM, 0.10,
    )
    guna_default = (0.33, 0.34, 0.33)
    purity_case = _build_guna_case_sql(
        GUNA_BY_ORDER, GUNA_BY_CLASS, GUNA_BY_PHYLUM, GUNA_BY_KINGDOM, guna_default, 0,
    )
    passion_case = _build_guna_case_sql(
        GUNA_BY_ORDER, GUNA_BY_CLASS, GUNA_BY_PHYLUM, GUNA_BY_KINGDOM, guna_default, 1,
    )
    ignorance_case = _build_guna_case_sql(
        GUNA_BY_ORDER, GUNA_BY_CLASS, GUNA_BY_PHYLUM, GUNA_BY_KINGDOM, guna_default, 2,
    )
    return f"""UPDATE species SET
    mobility_score = {mobility_case},
    warm_blood_score = {warm_blood_case},
    size_score = {size_case},
    purity_score = {purity_case},
    passion_score = {passion_case},
    ignorance_score = {ignorance_case}
"""


# ═══════════════════════════════════════════════════════════════════════
#  MIGRATION
# ═══════════════════════════════════════════════════════════════════════

ALL_TRAIT_COLS = (
    "mobility_score", "warm_blood_score", "size_score",
    "purity_score", "passion_score", "ignorance_score",
)


def migrate_species_traits(db_dir: str | None = None) -> int:
    """Add all trait columns to every species DB file and populate them."""
    import sqlite3
    db_files = list_species_db_files(db_dir)
    if not db_files:
        logger.warning("No species DB files found.")
        return 0

    update_sql = build_trait_update_sql()
    total_updated = 0

    for i, db_path in enumerate(db_files, 1):
        logger.info("  [%d/%d] Migrating %s ...", i, len(db_files), db_path)

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=OFF")

        existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(species)")}
        for col in ALL_TRAIT_COLS:
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE species ADD COLUMN {col} REAL DEFAULT 0.0")

        cursor = conn.execute(update_sql)
        updated = cursor.rowcount
        total_updated += updated

        conn.commit()
        conn.close()
        logger.info("    Updated %d rows", updated)

    logger.info("Trait migration complete. %d rows updated across %d files.",
                total_updated, len(db_files))

    # Rebuild precomputed stats cache
    logger.info("Building stats cache...")
    from src.db.species_queries import build_stats_cache
    build_stats_cache(db_dir)

    return total_updated
