"""Sheet logic for practice sheets: modes, fretboard mapping, 6×4 grid."""

import random
from dataclasses import dataclass
from typing import Optional

# Standard tuning: semitone offset from low E open (string 0 = E, 1 = A, 2 = D, 3 = G, 4 = B, 5 = E)
STANDARD_TUNING_OFFSETS = [0, 5, 10, 15, 19, 24]

# Root note: name and semitone offset from E (E=0, F=1, F#=2, ...)
ROOT_NOTE = "F"
ROOT_OFFSET = 1  # F is 1 semitone above E

# Mode: semitone offset from root -> scale degree (1-7)
IONIAN = {0: 1, 2: 2, 4: 3, 5: 4, 7: 5, 9: 6, 11: 7}  # E F# G# A B C# D#
AEOLIAN = {0: 1, 2: 2, 3: 3, 5: 4, 7: 5, 8: 6, 10: 7}  # E F# G A B C D

MODES = {
    "Ionian": IONIAN,
    "Aeolian": AEOLIAN,
}

ROWS = 6
COLS = 4
FRETS = list(range(COLS))  # 0, 1, 2, 3


@dataclass
class GridData:
    """Structured output for PDF export."""

    mode: str
    degrees: list[int]
    root_note: str
    grid: list[list[Optional[int]]]  # 6 rows × 4 cols; cell = fret number or None


def _semitone_to_degree(semitone: int, mode_map: dict[int, int]) -> Optional[int]:
    """Map pitch class (semitone 0-11 from root) to scale degree 1-7, or None if not in scale."""
    semitone_from_root = (semitone - ROOT_OFFSET) % 12
    return mode_map.get(semitone_from_root)


def generate(seed: Optional[int] = None) -> GridData:
    """
    Generate a 6×4 practice grid (root F, frets 0-3).
    Returns mode name, three chosen scale degrees, root note, and grid (fret number or blank).
    """
    if seed is not None:
        random.seed(seed)

    mode_name = random.choice(list(MODES.keys()))
    mode_map = MODES[mode_name]
    degrees = sorted(random.sample(range(1, 8), 3))

    grid: list[list[Optional[int]]] = []
    for row in range(ROWS):
        grid_row: list[Optional[int]] = []
        for col in range(COLS):
            fret = col
            semitone = (STANDARD_TUNING_OFFSETS[row] + fret) % 12
            degree = _semitone_to_degree(semitone, mode_map)
            if degree is not None and degree in degrees:
                grid_row.append(fret)
            else:
                grid_row.append(None)
        grid.append(grid_row)

    return GridData(
        mode=mode_name,
        degrees=degrees,
        root_note=ROOT_NOTE,
        grid=grid,
    )
