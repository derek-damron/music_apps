"""Export practice sheet content to PDF using reportlab."""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

from apps.practice_sheets.generator import GridData

PAGE_WIDTH, PAGE_HEIGHT = letter


def export_to_pdf(_: GridData, path: str | Path) -> None:
    """
    Render a one-page blank practice sheet template.

    Layout:
    - Top third: week focus area (3 lines) on the left and a fretboard outline on the right.
    - Bottom two thirds: Sunday–Saturday labels on the left, each with 3 note lines on the right.
    """
    path = Path(path)
    c = canvas.Canvas(str(path), pagesize=letter)

    # Page and layout geometry
    margin = 0.75 * inch
    content_width = PAGE_WIDTH - 2 * margin
    page_top = PAGE_HEIGHT - margin
    page_bottom = margin
    usable_height = page_top - page_bottom

    top_section_height = usable_height / 3
    bottom_section_height = usable_height - top_section_height

    top_section_top = page_top
    top_section_bottom = top_section_top - top_section_height

    bottom_section_top = top_section_bottom
    bottom_section_bottom = page_bottom

    left_col_width = content_width / 3
    right_col_width = content_width - left_col_width

    left_col_x = margin
    right_col_x = left_col_x + left_col_width

    col_padding = 0.1 * inch

    # --- Top third: left week focus area (3 lines) ---
    c.setFont("Helvetica-Bold", 12)
    focus_label_x = left_col_x + col_padding
    focus_label_y = top_section_top - col_padding
    c.drawString(focus_label_x, focus_label_y, "Week Focus Area")

    focus_line_start_x = focus_label_x
    focus_line_end_x = left_col_x + left_col_width - col_padding
    focus_line_spacing = 0.3 * inch

    first_line_y = focus_label_y - 0.35 * inch
    for i in range(3):
        y = first_line_y - i * focus_line_spacing
        c.line(focus_line_start_x, y, focus_line_end_x, y)

    # --- Top third: right fretboard outline ---
    c.setFont("Helvetica-Bold", 12)  # same style/size as Week Focus Area
    fretboard_label_x = right_col_x + col_padding
    fretboard_label_y = top_section_top - col_padding
    c.drawString(fretboard_label_x, fretboard_label_y, "Fretboard")

    fretboard_left_full = right_col_x + col_padding
    fretboard_right_full = margin + content_width - col_padding
    label_to_grid_gap = 0.25 * inch
    fretboard_top_full = fretboard_label_y - label_to_grid_gap
    fretboard_bottom_full = top_section_bottom + col_padding

    fretboard_height_full = fretboard_top_full - fretboard_bottom_full
    fretboard_width_full = fretboard_right_full - fretboard_left_full

    # Span full width; keep row height from 6-string layout, add one row (7 strings)
    fretboard_left = fretboard_left_full
    fretboard_right = fretboard_right_full
    fretboard_width = fretboard_width_full
    fretboard_top = fretboard_top_full

    string_count_original = 6
    row_height = fretboard_height_full * (2 / 3) / (string_count_original - 1)
    string_count = 7
    fretboard_height = row_height * (string_count - 1)
    fretboard_bottom = fretboard_top - fretboard_height

    if string_count > 1:
        string_spacing = fretboard_height / (string_count - 1)
    else:
        string_spacing = 0

    for i in range(string_count):
        y = fretboard_bottom + i * string_spacing
        c.line(fretboard_left, y, fretboard_right, y)

    fret_count = 16
    fret_spacing = fretboard_width / fret_count
    for j in range(fret_count + 1):
        x = fretboard_left + j * fret_spacing
        c.line(x, fretboard_bottom, x, fretboard_top)

    # --- Bottom two thirds: days of week and note lines ---
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    num_days = len(days)

    available_height_bottom = bottom_section_top - bottom_section_bottom
    block_height = available_height_bottom / num_days

    day_font_size = 12  # ~20% larger than base 10
    note_line_spacing = focus_line_spacing  # match Week Focus Area spacing (0.3 inch)
    c.setFont("Helvetica-Bold", day_font_size)

    day_label_x = left_col_x + col_padding
    note_line_start_x = right_col_x + col_padding
    note_line_end_x = margin + content_width - col_padding

    for index, day in enumerate(days):
        block_top = bottom_section_top - index * block_height
        block_bottom = block_top - block_height

        # Align day label vertically with first note line; use same spacing as Week Focus Area
        line1_y = block_top - 0.2 * block_height
        line2_y = line1_y - note_line_spacing
        line3_y = line2_y - note_line_spacing

        if line3_y < block_bottom:
            # Clamp so all lines stay within the block
            overflow = block_bottom - line3_y
            line1_y += overflow
            line2_y += overflow
            line3_y += overflow

        day_label_y = line1_y  # align day label with first note line
        c.drawString(day_label_x, day_label_y, day)

        c.line(note_line_start_x, line1_y, note_line_end_x, line1_y)
        c.line(note_line_start_x, line2_y, note_line_end_x, line2_y)
        c.line(note_line_start_x, line3_y, note_line_end_x, line3_y)

    c.save()