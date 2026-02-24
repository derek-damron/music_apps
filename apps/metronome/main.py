"""CLI (and optional serve) entrypoint for metronome app."""

import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple metronome")
    parser.add_argument("--bpm", type=int, default=120, help="Beats per minute")
    parser.add_argument("--serve", action="store_true", help="Run as server (for ECS)")
    args = parser.parse_args()
    if args.serve:
        _serve(bpm=args.bpm)
    else:
        _run_metronome(bpm=args.bpm)


def _run_metronome(bpm: int) -> None:
    # TODO: play click at bpm (e.g. sounddevice, pygame, or terminal beep)
    print(f"Metronome: {bpm} BPM (not yet implemented)", file=sys.stderr)


def _serve(bpm: int) -> None:
    # TODO: run HTTP/WebSocket server for remote metronome (e.g. FastAPI)
    print(f"Serve mode: {bpm} BPM (not yet implemented)", file=sys.stderr)


if __name__ == "__main__":
    main()
