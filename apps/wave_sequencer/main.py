"""CLI and Lambda entrypoint for wave sequencer app."""

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create sound files from a sequence of wave frequencies and durations"
    )
    parser.add_argument("--output", "-o", default="output.wav", help="Output WAV path")
    parser.add_argument(
        "sequence",
        nargs="*",
        metavar="FREQ:DUR",
        help="Pairs like 440:0.5 (frequency in Hz, duration in seconds)",
    )
    args = parser.parse_args()
    # TODO: parse sequence, call synthesizer, write WAV
    print(f"Wave sequencer: output={args.output}, sequence={args.sequence}", file=sys.stderr)
    print("Not yet implemented.")


def lambda_handler(event: dict, context: object) -> dict:
    """AWS Lambda entrypoint. Reuses same logic as CLI."""
    # TODO: parse event (sequence + output), generate WAV, upload to S3 or return URL
    return {"statusCode": 501, "body": "Not yet implemented"}


if __name__ == "__main__":
    main()
