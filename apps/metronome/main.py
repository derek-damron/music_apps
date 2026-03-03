"""CLI (and optional serve) entrypoint for metronome app."""

import argparse
import json
import math
import sys
import threading
import time
from typing import Optional

DEBUG_LOG = "/Users/derek/git/music_apps/.cursor/debug.log"


def _debug_log(message: str, data: Optional[dict] = None, hypothesis_id: Optional[str] = None) -> None:
    # region agent log
    try:
        payload = {
            "id": f"log_{int(time.time() * 1000)}",
            "timestamp": int(time.time() * 1000),
            "location": "main.py",
            "message": message,
            "data": data or {},
        }
        if hypothesis_id:
            payload["hypothesisId"] = hypothesis_id
        with open(DEBUG_LOG, "a") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception:
        pass
    # endregion

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


def _format_elapsed(seconds: float) -> str:
    """Format elapsed seconds as MM:SS or H:MM:SS."""
    total = int(seconds)
    if total < 3600:
        m, s = divmod(total, 60)
        return f"{m}:{s:02d}"
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    return f"{h}:{m:02d}:{s:02d}"


def _run_metronome(bpm: int) -> None:
    interval = 60.0 / bpm
    sample_rate = 44100
    click_duration_sec = 0.02
    click_samples = _generate_click(
        duration_sec=click_duration_sec,
        frequency=1000.0,
        sample_rate=sample_rate,
    )

    stop_event = threading.Event()
    start = time.perf_counter()

    def _timer_thread() -> None:
        print(f"\r0:00 @ {bpm} BPM", end="", flush=True)
        while not stop_event.is_set():
            # Wait up to 1s so we wake immediately when stop_event is set (avoids ~1s delay on Ctrl+C)
            stop_event.wait(timeout=1.0)
            if stop_event.is_set():
                _debug_log("timer_exiting", {"perf": time.perf_counter() - start}, "H1")
                break
            elapsed = time.perf_counter() - start
            print(f"\r{_format_elapsed(elapsed)} @ {bpm} BPM", end="", flush=True)

    timer = threading.Thread(target=_timer_thread, daemon=True)
    timer.start()

    def _beep_loop() -> None:
        try:
            while not stop_event.is_set():
                sys.stdout.write("\a")
                sys.stdout.flush()
                time.sleep(interval)
        except KeyboardInterrupt:
            pass

    try:
        if sounddevice is None:
            print("sounddevice not installed; using terminal beep (install sounddevice for proper click)", file=sys.stderr)
            _beep_loop()
        else:
            try:
                while not stop_event.is_set():
                    t0 = time.perf_counter()
                    sounddevice.play(click_samples, samplerate=sample_rate, blocking=True)
                    elapsed = time.perf_counter() - t0
                    time.sleep(max(0.0, interval - elapsed))
            except sounddevice.PortAudioError:
                print("No audio device available; using terminal beep", file=sys.stderr)
                _beep_loop()
    except KeyboardInterrupt:
        pass
    finally:
        t0_finally = time.perf_counter()
        _debug_log("finally_entered", {"perf": t0_finally - start}, "H2")
        stop_event.set()
        timer.join(timeout=1.0)
        t_after_join = time.perf_counter()
        _debug_log("join_returned", {"perf": t_after_join - start, "join_duration": t_after_join - t0_finally, "timer_alive": timer.is_alive()}, "H2")
        print()


def _serve(bpm: int) -> None:
    # TODO: run HTTP/WebSocket server for remote metronome (e.g. FastAPI)
    print(f"Serve mode: {bpm} BPM (not yet implemented)", file=sys.stderr)


if __name__ == "__main__":
    main()
