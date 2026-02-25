"""CLI entrypoint for practice sheets app (local Python only)."""

import argparse
import sys

from apps.practice_sheets import generator
from apps.practice_sheets import pdf_export


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate guitar practice sheets and export as PDF")
    parser.add_argument("--output", "-o", default="practice_sheet.pdf", help="Output PDF path")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible sheets")
    args = parser.parse_args()

    grid_data = generator.generate(seed=args.seed)
    pdf_export.export_to_pdf(grid_data, args.output)
    print(f"Wrote {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
