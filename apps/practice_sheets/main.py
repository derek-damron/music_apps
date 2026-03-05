"""CLI entrypoint for practice sheets app (local Python only)."""

import argparse
import os
import sys
from pathlib import Path

from apps.practice_sheets import generator
from apps.practice_sheets import pdf_export

_DEFAULT_PDF_DIR = os.environ.get("MUSIC_APPS_PDF_DIR", "pdf")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate guitar practice sheets and export as PDF")
    parser.add_argument(
        "--output",
        "-o",
        default=str(Path(_DEFAULT_PDF_DIR) / "practice_sheet.pdf"),
        help="Output PDF path (default: %(default)s)",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible sheets")
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    grid_data = generator.generate(seed=args.seed)
    pdf_export.export_to_pdf(grid_data, output_path)
    print(f"Wrote {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
