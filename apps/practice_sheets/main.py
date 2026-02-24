"""CLI and Lambda entrypoint for practice sheets app."""

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate guitar practice sheets and export as PDF")
    parser.add_argument("--output", "-o", default="practice_sheet.pdf", help="Output PDF path")
    parser.add_argument("--bpm", type=int, default=80, help="Tempo (BPM)")
    args = parser.parse_args()
    # TODO: call generator + pdf_export
    print(f"Practice sheets: output={args.output}, bpm={args.bpm}", file=sys.stderr)
    print("Not yet implemented.")


def lambda_handler(event: dict, context: object) -> dict:
    """AWS Lambda entrypoint. Reuses same logic as CLI."""
    # TODO: parse event, generate sheet, upload to S3 or return base64 PDF
    return {"statusCode": 501, "body": "Not yet implemented"}


if __name__ == "__main__":
    main()
