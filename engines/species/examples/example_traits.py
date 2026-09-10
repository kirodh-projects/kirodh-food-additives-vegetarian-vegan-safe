"""Compute heuristic trait scores for a taxonomic group (no database needed).

Run:
    python -m engines.species.examples.example_traits --kingdom Animalia --phylum Chordata --class Mammalia --order Carnivora
    python -m engines.species.examples.example_traits --kingdom Plantae --phylum Tracheophyta --class Magnoliopsida --order \"\"
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Trait heuristics (pure functions).")
    parser.add_argument("--kingdom", default="Animalia")
    parser.add_argument("--phylum", default="Chordata")
    parser.add_argument("--class", dest="class_name", default="Mammalia")
    parser.add_argument("--order", dest="order_name", default="Carnivora")
    args = parser.parse_args(argv)

    from ..traits import compute_gunas, compute_mobility, compute_size, compute_warm_blood

    mob = compute_mobility(args.kingdom, args.phylum, args.class_name, args.order_name)
    warm = compute_warm_blood(args.kingdom, args.phylum, args.class_name, args.order_name)
    size = compute_size(args.kingdom, args.phylum, args.class_name, args.order_name)
    sattva, rajas, tamas = compute_gunas(args.kingdom, args.phylum, args.class_name, args.order_name)
    print(f"group: {args.kingdom} > {args.phylum} > {args.class_name} > {args.order_name or '(none)'}")
    print(f"mobility   : {mob:.3f}  (0=sessile, 1=highly mobile)")
    print(f"warm-blood : {warm:.3f}  (0=ectotherm, 1=endotherm)")
    print(f"size       : {size:.3f}  (0=microscopic, 1=largest)")
    print(f"gunas      : sattva={sattva:.3f} rajas={rajas:.3f} tamas={tamas:.3f} (sum={sattva + rajas + tamas:.3f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
