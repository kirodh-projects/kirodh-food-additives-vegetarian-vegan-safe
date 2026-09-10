"""Classification constants: keyword lists and known E-number lookup tables."""

# ---------------------------------------------------------------------------
# Known E-number classifications (Tier 1 - highest confidence)
# Each entry: {"vegan": ..., "vegetarian": ..., "origin": ..., "safety": ...}
# vegetarian = lacto-vegetarian (dairy OK, eggs NOT OK)
# ---------------------------------------------------------------------------
KNOWN_CLASSIFICATIONS: dict[str, dict[str, str]] = {
    # --- Definitely NOT vegan and NOT vegetarian (animal death / insect-derived) ---
    "E120": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Cochineal/carmine - crushed cochineal insects",
    },
    "E441": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Gelatin from animal bones/hides",
    },
    "E428": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Gelatin from animal bones/hides",
    },
    "E542": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Bone phosphate from animal bones",
    },
    "E904": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Shellac from lac insects",
    },
    "E920": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "L-cysteine often from animal hair/feathers",
    },
    "E921": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "L-cystine often from animal hair/feathers",
    },
    "E631": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Disodium inosinate - often from meat/fish",
    },
    "E635": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Disodium 5'-ribonucleotides - from animal tissue",
    },
    "E640": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Glycine - often from animal sources",
    },
    "E910": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "L-cysteine from duck feathers",
    },
    "E1000": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Cholic acid from cow bile",
    },

    # --- NOT vegan, but vegetarian OK (dairy/bee products, no killing) ---
    "E901": {
        "vegan": "No", "vegetarian": "Yes",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Beeswax - bee product, no killing required",
    },
    "E966": {
        "vegan": "No", "vegetarian": "Yes",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Lactitol from lactose (milk sugar)",
    },
    "E270": {
        "vegan": "No", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Lactic acid - can be from milk fermentation",
    },
    "E325": {
        "vegan": "No", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Sodium lactate - may derive from milk",
    },
    "E326": {
        "vegan": "No", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Potassium lactate - may derive from milk",
    },
    "E327": {
        "vegan": "No", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Calcium lactate - may derive from milk",
    },

    # --- NOT vegan, NOT vegetarian (egg-derived -> lacto-veg says no eggs) ---
    "E322": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Lecithin - often from eggs or soy; eggs not lacto-vegetarian",
    },
    "E1105": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Lysozyme from egg whites",
    },

    # --- Vegan and vegetarian (plant/synthetic) ---
    "E100": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Curcumin from turmeric",
    },
    "E101": {
        "vegan": "Maybe", "vegetarian": "Maybe",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Riboflavin - can be synthetic or from eggs/milk",
    },
    "E102": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Tartrazine - synthetic azo dye, can cause hyperactivity",
    },
    "E104": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Avoid",
        "reason": "Quinoline Yellow - potentially carcinogenic",
    },
    "E110": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Sunset Yellow FCF - synthetic azo dye",
    },
    "E129": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Allura Red AC - from petroleum",
    },
    "E140": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Chlorophyll from plants",
    },
    "E150a": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Plain caramel - from heated sugar",
    },
    "E160a": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Carotenes from plants",
    },
    "E160b": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Annatto from seeds",
    },
    "E162": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Beetroot red / betanin",
    },
    "E170": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Mineral)",
        "safety": "Safe",
        "reason": "Calcium carbonate - mineral",
    },
    "E200": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Sorbic acid - synthetic preservative",
    },
    "E202": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Potassium sorbate",
    },
    "E210": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Caution",
        "reason": "Benzoic acid - can trigger asthma/allergies",
    },
    "E211": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Sodium benzoate - can form benzene with ascorbic acid",
    },
    "E220": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Sulphur dioxide - can trigger asthma",
    },
    "E250": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Sodium nitrite - safe in regulated amounts, potentially carcinogenic in excess",
    },
    "E251": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Sodium nitrate",
    },
    "E252": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Potassium nitrate",
    },
    "E300": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Ascorbic acid (Vitamin C)",
    },
    "E306": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Natural tocopherols (Vitamin E)",
    },
    "E307": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Alpha-tocopherol (synthetic Vitamin E)",
    },
    "E330": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Citric acid - from citrus or fermentation",
    },
    "E331": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Sodium citrate",
    },
    "E332": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Potassium citrate",
    },
    "E333": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Calcium citrate",
    },
    "E334": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Tartaric acid from grapes",
    },
    "E336": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Potassium tartrate (cream of tartar)",
    },
    "E338": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Phosphoric acid - mineral-derived",
    },
    "E400": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Alginic acid from seaweed",
    },
    "E406": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Agar from seaweed",
    },
    "E407": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Carrageenan from seaweed",
    },
    "E410": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Locust bean gum / carob gum",
    },
    "E412": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Guar gum from guar beans",
    },
    "E414": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Gum arabic / acacia gum",
    },
    "E415": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Xanthan gum - bacterial fermentation",
    },
    "E440": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Pectin from fruit",
    },
    "E450": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Diphosphates - synthetic mineral",
    },
    "E460": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Cellulose from wood pulp/cotton",
    },
    "E461": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Methyl cellulose",
    },
    "E466": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Carboxymethyl cellulose",
    },
    "E471": {
        "vegan": "Maybe", "vegetarian": "Maybe",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Mono- and diglycerides - can be from animal or plant fats",
    },
    "E472a": {
        "vegan": "Maybe", "vegetarian": "Maybe",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Acetic acid esters of mono/diglycerides - fat source uncertain",
    },
    "E500": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Mineral)",
        "safety": "Safe",
        "reason": "Sodium carbonates / baking soda",
    },
    "E501": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Mineral)",
        "safety": "Safe",
        "reason": "Potassium carbonates",
    },
    "E503": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Ammonium carbonates",
    },
    "E509": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Mineral)",
        "safety": "Safe",
        "reason": "Calcium chloride - mineral salt",
    },
    "E551": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Mineral)",
        "safety": "Safe",
        "reason": "Silicon dioxide - mineral",
    },
    "E570": {
        "vegan": "Maybe", "vegetarian": "Maybe",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Stearic acid - can be animal or plant fat",
    },
    "E621": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "MSG - typically from bacterial fermentation",
    },
    "E627": {
        "vegan": "No", "vegetarian": "No",
        "origin": "Natural (Animal)",
        "safety": "Safe",
        "reason": "Disodium guanylate - often from fish",
    },
    "E903": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Carnauba wax from palm leaves",
    },
    "E950": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Acesulfame K - synthetic sweetener",
    },
    "E951": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Aspartame - controversial, some sensitivity",
    },
    "E952": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Cyclamate - banned in US, permitted in EU",
    },
    "E953": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Isomalt - synthetic sugar alcohol",
    },
    "E954": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Caution",
        "reason": "Saccharin - synthetic sweetener",
    },
    "E955": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Sucralose - synthetic sweetener",
    },
    "E960": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Steviol glycosides from stevia plant",
    },
    "E965": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Synthetic",
        "safety": "Safe",
        "reason": "Maltitol - synthetic sugar alcohol",
    },
    "E967": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Natural (Plant)",
        "safety": "Safe",
        "reason": "Xylitol from birch or corn",
    },
    "E968": {
        "vegan": "Yes", "vegetarian": "Yes",
        "origin": "Mixed",
        "safety": "Safe",
        "reason": "Erythritol - from fermentation",
    },
}

# ---------------------------------------------------------------------------
# Keyword lists for Tier 2 text-based classification
# ---------------------------------------------------------------------------

# Animal-derived keywords that mean NOT vegan (multi-word to avoid false positives)
NON_VEGAN_KEYWORDS: list[str] = [
    "pancreas of pigs", "pig pancreas", "animal origin",
    "animal bones", "obtained from insects", "insect",
    "cochineal", "carmine", "gelatin", "gelatine",
    "collagen", "bone", "tendons", "ligaments",
    "hides of pig", "hides of calf", "shellac", "keratin",
    "chitin", "chitosan", "animal fat", "tallow", "suet", "lard",
    "fish oil", "cod liver", "crustacean", "feather", "hair",
    "slaughterhouse", "blood meal", "rennet",
    "animal tissue", "cow bile", "ox bile",
]

# Keywords meaning NOT vegetarian (involves killing - subset of non-vegan)
# Note: lacto-vegetarian, so eggs are also excluded
NON_VEGETARIAN_KEYWORDS: list[str] = [
    "pancreas of pigs", "pig pancreas", "animal bones", "bone",
    "obtained from insects", "insect", "cochineal", "carmine",
    "gelatin", "gelatine", "collagen", "tendons", "ligaments",
    "hides of pig", "hides of calf", "shellac",
    "slaughterhouse", "tallow", "suet", "lard",
    "blood meal", "crustacean", "fish",
    "animal tissue", "cow bile", "ox bile", "rennet",
]

# Egg-derived keywords: NOT vegetarian in lacto-vegetarian definition
EGG_KEYWORDS: list[str] = [
    "egg white", "egg yolk", "egg", "albumin", "lysozyme",
    "ovalbumin", "ovomucin",
]

# Dairy-derived: NOT vegan, but IS vegetarian (lacto-veg allows dairy)
DAIRY_KEYWORDS: list[str] = [
    "milk", "lactose", "casein", "whey", "dairy",
    "butter", "cream", "cheese", "lactate",
]

# Bee products: NOT vegan, but IS vegetarian (no killing)
BEE_KEYWORDS: list[str] = [
    "beeswax", "honey", "propolis", "royal jelly",
]

# Ambiguous origin - could be animal or plant
AMBIGUOUS_ORIGIN_KEYWORDS: list[str] = [
    "animal or vegetable", "animal or plant",
    "can be of animal", "may be of animal",
    "animal fats, including pork, is not totally excluded",
    "glycerides", "stearic", "fatty acid esters",
    "mono- and diglycerides",
]

# Context exclusions: mentions of "animal" that do NOT indicate animal origin
ANIMAL_CONTEXT_EXCLUSIONS: list[str] = [
    "laboratory animals", "test animals", "in animals",
    "effects in animals", "observed in animals",
    "carcinogenic in animals", "damage in animals",
    "tumors in animals", "studies in animals",
    "trials in animals", "experiments in animals",
    "toxicity in animals", "tested on animals",
]

# Safety keywords
SAFETY_AVOID_KEYWORDS: list[str] = [
    "carcinogen", "carcinogenic", "mutagenic", "teratogenic",
    "toxic", "neurotoxic", "reprotoxic",
    "potentially carcinogenic",
]

SAFETY_BANNED_KEYWORDS: list[str] = [
    "banned", "prohibited", "delisted",
]

SAFETY_CAUTION_KEYWORDS: list[str] = [
    "allergic", "allergy", "hyperactivity", "asthma",
    "harmful", "damage", "side effect", "intolerance",
    "eczema", "insomnia", "nausea", "irritation",
]

SAFETY_SAFE_KEYWORDS: list[str] = [
    "no side effects", "no known side effects", "no adverse",
    "generally recognized as safe", "gras",
    "no side effects have been found",
    "no known secondary effect",
]

# Origin keywords
SYNTHETIC_KEYWORDS: list[str] = [
    "synthetic", "artificial", "coal tar", "petroleum",
    "petrochemical", "azo dye", "produced artificially",
    "chemical synthesis", "chemically", "industrially produced",
]

NATURAL_PLANT_KEYWORDS: list[str] = [
    "plant", "vegetable", "turmeric", "fruit", "seed",
    "bark", "root", "tree", "algae", "seaweed", "fungi", "fungus",
    "yeast", "ferment", "starch", "cellulose", "pectin",
    "gum", "bean", "corn", "soy", "wheat", "rice",
]

NATURAL_MINERAL_KEYWORDS: list[str] = [
    "mineral", "calcium carbonate", "limestone", "chalk",
    "silicate", "iron oxide", "calcium chloride",
    "sodium chloride", "potassium chloride",
]

NATURAL_ANIMAL_KEYWORDS: list[str] = [
    "animal", "pig", "pork", "beef", "cow", "cattle",
    "insect", "bone", "hide", "gelatin", "gelatine",
    "shellac", "beeswax", "cochineal", "carmine",
    "lanolin", "wool",
]

# Category normalization map
CATEGORY_MAP: dict[str, str] = {
    "coloring": "Colouring",
    "color": "Colouring",
    "colour": "Colouring",
    "colours": "Colouring",
    "coulours": "Colouring",
    "yellow-orange": "Colouring",
    "yellow": "Colouring",
    "brown": "Colouring",
    "purple": "Colouring",
    "red": "Colouring",
    "blue": "Colouring",
    "green": "Colouring",
    "orange": "Colouring",
    "crimson": "Colouring",
    "black": "Colouring",
    "preservative": "Preservative",
    "antioxidant": "Antioxidant",
    "antioxidants": "Antioxidant",
    "anti-oxydant": "Antioxidant",
    "emulsifier": "Emulsifier",
    "emulsifiers": "Emulsifier",
    "stabiliser": "Stabiliser",
    "stabilizer": "Stabiliser",
    "thickener": "Thickener",
    "thickening agent": "Thickener",
    "gelling agent": "Thickener",
    "sweetener": "Sweetener",
    "acidity regulator": "Acidity Regulator",
    "acidulant": "Acidity Regulator",
    "raising agent": "Acidity Regulator",
    "anticaking agent": "Anti-caking Agent",
    "anti-caking agent": "Anti-caking Agent",
    "flour treatment agent": "Flour Treatment Agent",
    "flour bleaching agent": "Flour Treatment Agent",
    "improving agent": "Flour Treatment Agent",
    "glazing agent": "Glazing Agent",
    "coating agent": "Glazing Agent",
    "flavour enhancer": "Flavour Enhancer",
    "flavoring": "Flavour Enhancer",
    "propellant": "Propellant/Gas",
    "packaging gas": "Propellant/Gas",
    "antibiotic": "Antibiotic",
    "humectant": "Humectant",
    "sequestrant": "Sequestrant",
    "foaming agent": "Foaming Agent",
    "bulking agent": "Bulking Agent",
    "carrier": "Carrier",
    "solvent": "Carrier",
    "antifoam": "Miscellaneous",
}

# ADI extraction patterns
ADI_PATTERNS: list[str] = [
    r"ADI[:\s]+([^\.\n]+)",
    r"acceptable daily intake[:\s]+([^\.\n]+)",
    r"daily intake[:\s]+of\s+([^\.\n]+)",
    r"(\d+[\.\d]*\s*mg/kg\s*(?:body weight|bw|b\.w\.))",
]
