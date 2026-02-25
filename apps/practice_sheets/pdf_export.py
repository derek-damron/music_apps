"""Export practice sheet content to PDF using reportlab."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

from apps.practice_sheets.generator import GridData

PAGE_WIDTH, PAGE_HEIGHT = letter
HALF_HEIGHT = PAGE_HEIGHT / 2


def export_to_pdf(grid_data: GridData, path: str | Path) -> None:
    """
    Render one page: header and 6×4 grid, then numbers 1–7 each with 3 full-width lines
    filling the remainder of the page.
    """
    path = Path(path)
    c = canvas.Canvas(str(path), pagesize=letter)

    # --- Top half (upper 50%): y from HALF_HEIGHT to PAGE_HEIGHT ---
    top_y_start = HALF_HEIGHT
    margin = 0.75 * inch
    content_width = PAGE_WIDTH - 2 * margin

    # Scale name (e.g. "Ionian" or "Aeolian")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, top_y_start + (HALF_HEIGHT - 0.5 * inch), f"{grid_data.mode} (root {grid_data.root_note})")

    # 6×4 grid: rows = strings (row 1 = low E), columns = frets 0–3
    # Build table data: header row = fret numbers; then 6 rows (low E to high E)
    table_data = [["", "0", "1", "2", "3"]]
    string_labels = ["Low E", "A", "D", "G", "B", "High E"]
    for row_idx, row in enumerate(grid_data.grid):
        str_label = string_labels[row_idx]
        cells = [str_label]
        for cell in row:
            cells.append(str(cell) if cell is not None else "—")
        table_data.append(cells)

    col_width = content_width / 5
    row_height = 0.25 * inch
    t = Table(table_data, colWidths=[col_width] * 5, rowHeights=[row_height] * 7)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    table_height = 7 * row_height
    table_y = top_y_start + (HALF_HEIGHT - 0.5 * inch - 0.3 * inch - table_height)
    t.wrapOn(c, content_width, table_height)
    t.drawOn(c, margin, table_y)

    # Practice days 1–7: label then each number + 3 full-width lines, filling remainder of page
    num_blocks = 7
    left_x = margin
    right_x = PAGE_WIDTH - margin
    label_space = 0.35 * inch
    section_top = table_y - label_space
    c.setFont("Helvetica", 10)
    c.drawString(left_x, table_y - 0.2 * inch, "Practice days:")
    available_height = section_top - margin
    block_height = available_height / num_blocks
    line_spacing_notes = 0.2 * inch
    for i in range(num_blocks):
        block_top = section_top - i * block_height
        number_y = block_top - 0.15 * inch
        line1_y = number_y - 0.15 * inch
        line2_y = line1_y - line_spacing_notes
        line3_y = line2_y - line_spacing_notes
        c.drawString(left_x, number_y, str(i + 1))
        c.line(left_x, line1_y, right_x, line1_y)
        c.line(left_x, line2_y, right_x, line2_y)
        c.line(left_x, line3_y, right_x, line3_y)

    c.save()