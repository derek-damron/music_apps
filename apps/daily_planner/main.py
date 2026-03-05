"""CLI entrypoint for daily planner app."""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

from apps.daily_planner import pdf_export

_DEFAULT_PDF_DIR = os.environ.get("MUSIC_APPS_PDF_DIR", "pdf")


def _parse_date(s: str) -> date:
    """Parse YYYY-MM-DD to date."""
    return date.fromisoformat(s)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a daily planner PDF")
    parser.add_argument(
        "--output",
        "-o",
        default=str(Path(_DEFAULT_PDF_DIR) / "daily_planner.pdf"),
        help="Output PDF path (default: %(default)s)",
    )
    parser.add_argument(
        "--start-date",
        metavar="YYYY-MM-DD",
        type=_parse_date,
        default=None,
        help="Start date for work-week PDF (5 consecutive days). If omitted, generate single-day PDF.",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if args.start_date is not None:
        pdf_export.export_work_week_to_pdf(output_path, args.start_date)
    else:
        pdf_export.export_to_pdf(output_path)
    print(f"Wrote {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

