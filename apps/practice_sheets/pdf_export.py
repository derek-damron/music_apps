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
    Render one page: top half = scale name, 6×4 grid, numbers 1–7;
    bottom half = horizontal ruled lines for notes.
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

    # Numbers 1 2 3 4 5 6 7 for marking practice days
    c.setFont("Helvetica", 10)
    days_y = table_y - 0.35 * inch
    c.drawString(margin, days_y, "Practice days:")
    c.drawString(margin + 1.2 * inch, days_y, "1  2  3  4  5  6  7")

    # --- Bottom half (lower 50%): ruled lines for notes ---
    line_spacing = 0.35 * inch
    num_lines = int((HALF_HEIGHT - 2 * margin) / line_spacing)
    left_x = margin
    right_x = PAGE_WIDTH - margin
    y = HALF_HEIGHT - margin
    for _ in range(num_lines):
        c.line(left_x, y, right_x, y)
        y -= line_spacing

    c.save()