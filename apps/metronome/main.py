"""CLI (and optional serve) entrypoint for metronome app."""

import argparse
import math
import sys
import time

try:
    import sounddevice
except ImportError:
    sounddevice = None  # type: ignore[assignment]


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple metronome")
    parser.add_argument("--bpm", type=int, default=120, help="Beats per minute")
    parser.add_argument("--serve", action="store_true", help="Run as server (for ECS)")
    args = parser.parse_args()
    if args.serve:
        _serve(bpm=args.bpm)
    else:
        _run_metronome(bpm=args.bpm)


def _generate_click(
    duration_sec: float = 0.02,
    frequency: float = 1000.0,
    sample_rate: int = 44100,
) -> list[float]:
    """Generate a short click as float32 samples (sine burst with decay)."""
    n = int(duration_sec * sample_rate)
    samples = []
    for i in range(n):
        t = i / sample_rate
        sine = math.sin(2 * math.pi * frequency * t)
        # Quick decay so release doesn't click
        envelope = 1.0 - (i / n) ** 2
        samples.append(0.3 * sine * envelope)
    return samples


def _run_metronome(bpm: int) -> None:
    interval = 60.0 / bpm
    sample_rate = 44100
    click_duration_sec = 0.02
    click_samples = _generate_click(
        duration_sec=click_duration_sec,
        frequency=1000.0,
        sample_rate=sample_rate,
    )

    def _beep_loop() -> None:
        try:
            while True:
                sys.stdout.write("\a")
                sys.stdout.flush()
                time.sleep(interval)
        except KeyboardInterrupt:
            pass

    if sounddevice is None:
        print("sounddevice not installed; using terminal beep (install sounddevice for proper click)", file=sys.stderr)
        _beep_loop()
        return

    try:
        while True:
            t0 = time.perf_counter()
            sounddevice.play(click_samples, samplerate=sample_rate, blocking=True)
            elapsed = time.perf_counter() - t0
            time.sleep(max(0.0, interval - elapsed))
    except sounddevice.PortAudioError:
        print("No audio device available; using terminal beep", file=sys.stderr)
        _beep_loop()
    except KeyboardInterrupt:
        pass


def _serve(bpm: int) -> None:
    # TODO: run HTTP/WebSocket server for remote metronome (e.g. FastAPI)
    print(f"Serve mode: {bpm} BPM (not yet implemented)", file=sys.stderr)


if __name__ == "__main__":
    main()
