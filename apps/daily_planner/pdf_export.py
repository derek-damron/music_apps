"""Export a one-page daily planner template to PDF using reportlab."""

from datetime import date, timedelta
from pathlib import Path
from typing import Any

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = letter

# Single-letter weekdays for table header (Monday=0 .. Sunday=6)
_WEEKDAY_LETTERS = "MTWTFSS"

# Baseline offset for vertically centering 10pt text in table cells
_FONT_BASELINE_OFFSET = 4


def _compute_geometry() -> dict[str, Any]:
    """Compute layout geometry for one letter page (portrait)."""
    margin = 0.75 * inch
    content_width = PAGE_WIDTH - 2 * margin
    page_top = PAGE_HEIGHT - margin
    page_bottom = margin
    usable_height = page_top - page_bottom
    band_height = usable_height / 10.0

    return {
        "margin": margin,
        "content_width": content_width,
        "page_top": page_top,
        "page_bottom": page_bottom,
        "usable_height": usable_height,
        "band_height": band_height,
        "left_x": margin,
        "right_x": margin + content_width,
        "date_top": page_top,
        "date_bottom": page_top - band_height,
        "weekly_top": page_top - band_height,
        "weekly_bottom": page_top - 3 * band_height,
        "daily_top": page_top - 3 * band_height,
        "daily_bottom": page_bottom,
        "section_padding_x": 0.15 * inch,
        "line_spacing": 0.35 * inch,
        "left_panel_width": content_width * (2.0 / 3.0),
    }


def _draw_date_band_single(c: canvas.Canvas, geom: dict[str, Any]) -> None:
    """Draw the single-day date band: 'Date:' label + handwriting line."""
    left_x = geom["left_x"]
    right_x = geom["right_x"]
    date_top = geom["date_top"]
    band_height = geom["band_height"]
    section_padding_x = geom["section_padding_x"]

    c.setFont("Helvetica-Bold", 14)
    date_label = "Date:"
    date_label_x = left_x + section_padding_x
    date_label_y = date_top - 0.4 * band_height
    c.drawString(date_label_x, date_label_y, date_label)

    label_width = c.stringWidth(date_label, "Helvetica-Bold", 14)
    date_line_start_x = date_label_x + label_width + 0.25 * inch
    date_line_end_x = right_x - section_padding_x
    date_line_y = date_label_y - 2
    c.line(date_line_start_x, date_line_y, date_line_end_x, date_line_y)


def _draw_date_band_work_week(
    c: canvas.Canvas,
    geom: dict[str, Any],
    page_date: date,
    all_dates: list[date],
    destination_names: list[str],
    page_index: int,
) -> None:
    """Draw work-week date band: left = formatted date, right = 2-row table (M T W T F; 3/2 ...) with clickable date cells."""
    left_x = geom["left_x"]
    right_x = geom["right_x"]
    date_top = geom["date_top"]
    date_bottom = geom["date_bottom"]
    band_height = geom["band_height"]
    content_width = geom["content_width"]
    section_padding_x = geom["section_padding_x"]

    # Left half: "March 2, 2025"
    date_str = f"{page_date.strftime('%B')} {page_date.day}, {page_date.year}"
    c.setFont("Helvetica-Bold", 14)
    date_label_y = date_top - 0.4 * band_height
    c.drawString(left_x + section_padding_x, date_label_y, date_str)

    # Right half: table (header row = M,T,W,T,F; data row = 3/2, 3/3, ...)
    table_left = left_x + content_width / 2 + section_padding_x
    table_right = right_x - section_padding_x
    table_width = table_right - table_left
    table_top = date_top - 0.15 * band_height
    table_bottom = date_bottom + 0.1 * band_height
    table_height = table_top - table_bottom
    cell_width = table_width / 5
    header_row_height = table_height * 0.45
    data_row_height = table_height * 0.55
    data_row_top = table_top - header_row_height

    # Table borders: outer rect, current-day date-cell highlight, then vertical/horizontal dividers
    c.setLineWidth(0.8)
    c.rect(table_left, table_bottom, table_width, table_height, stroke=1, fill=0)
    # Highlight current day's date cell only (light gray fill, inset so borders stay unchanged)
    c.setFillColorRGB(0.9, 0.9, 0.9)
    highlight_inset = 0.5
    highlight_left = table_left + page_index * cell_width + highlight_inset
    highlight_bottom = table_bottom + highlight_inset
    highlight_width = cell_width - 2 * highlight_inset
    highlight_height = data_row_height - 2 * highlight_inset
    c.rect(highlight_left, highlight_bottom, highlight_width, highlight_height, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    for col in range(1, 5):
        x = table_left + col * cell_width
        c.line(x, table_bottom, x, table_top)
    c.line(table_left, data_row_top, table_right, data_row_top)

    # Header row: weekday letters (M, T, W, T, F, S, S), vertically centered
    c.setFont("Helvetica-Bold", 10)
    header_y = table_top - header_row_height / 2 - _FONT_BASELINE_OFFSET
    for col in range(5):
        cell_left = table_left + col * cell_width
        letter_str = _WEEKDAY_LETTERS[all_dates[col].weekday()]
        c.drawString(
            cell_left + cell_width / 2 - c.stringWidth(letter_str, "Helvetica-Bold", 10) / 2,
            header_y,
            letter_str,
        )

    # Data row: dates (3/2, etc.) and clickable link to that day's page, vertically centered
    c.setFont("Helvetica", 10)
    data_y = data_row_top - data_row_height / 2 - _FONT_BASELINE_OFFSET
    for col in range(5):
        cell_left = table_left + col * cell_width
        cell_right = cell_left + cell_width
        date_cell_str = f"{all_dates[col].month}/{all_dates[col].day}"
        c.drawString(
            cell_left + cell_width / 2 - c.stringWidth(date_cell_str, "Helvetica", 10) / 2,
            data_y,
            date_cell_str,
        )
        cell_rect = [cell_left, table_bottom, cell_right, data_row_top]
        link_tooltip = f"Go to {all_dates[col].month}/{all_dates[col].day}"
        c.linkRect(link_tooltip, destination_names[col], Rect=cell_rect, relative=1)


def _draw_rest_of_page(c: canvas.Canvas, geom: dict[str, Any]) -> None:
    """Draw weekly priorities, daily priorities, brain dump, and schedule (everything below the date band)."""
    left_x = geom["left_x"]
    right_x = geom["right_x"]
    weekly_top = geom["weekly_top"]
    weekly_bottom = geom["weekly_bottom"]
    daily_top = geom["daily_top"]
    daily_bottom = geom["daily_bottom"]
    section_padding_x = geom["section_padding_x"]
    line_spacing = geom["line_spacing"]
    left_panel_width = geom["left_panel_width"]

    left_panel_x = left_x
    left_panel_right_x = left_x + left_panel_width
    right_panel_x = left_panel_right_x
    right_panel_right_x = right_x
    right_panel_width = right_panel_right_x - right_panel_x
    left_panel_top = daily_top
    left_panel_bottom = daily_bottom
    left_panel_height = left_panel_top - left_panel_bottom
    left_mid_y = left_panel_top - left_panel_height / 2.0
    number_padding_x = 0.1 * inch

    # --- Top 3 weekly priorities ---
    c.setFont("Helvetica-Bold", 12)
    weekly_title_x = left_x + section_padding_x
    weekly_title_y = weekly_top - 0.25 * inch
    c.drawString(weekly_title_x, weekly_title_y, "Top 3 Weekly Priorities")
    priorities_first_line_y = weekly_title_y - 0.5 * inch

    for i in range(3):
        y = priorities_first_line_y - i * line_spacing
        if y < weekly_bottom + 0.2 * inch:
            break
        number_text = f"{i + 1}."
        c.drawString(weekly_title_x, y, number_text)
        num_width = c.stringWidth(number_text, "Helvetica-Bold", 12)
        line_start_x = weekly_title_x + num_width + number_padding_x
        c.line(line_start_x, y - 2, right_x - section_padding_x, y - 2)

    # --- Left 2/3: Today's top 3 priorities ---
    c.setFont("Helvetica-Bold", 12)
    today_title_x = left_panel_x + section_padding_x
    today_title_y = left_panel_top - 0.25 * inch
    c.drawString(today_title_x, today_title_y, "Today's Top 3 Priorities")
    today_first_line_y = today_title_y - 0.5 * inch

    for i in range(3):
        y = today_first_line_y - i * line_spacing
        if y < left_mid_y + 0.2 * inch:
            break
        number_text = f"{i + 1}."
        c.drawString(today_title_x, y, number_text)
        num_width = c.stringWidth(number_text, "Helvetica-Bold", 12)
        line_start_x = today_title_x + num_width + number_padding_x
        c.line(line_start_x, y - 2, left_panel_right_x - section_padding_x, y - 2)

    # --- End-of-day brain dump ---
    c.setFont("Helvetica-Bold", 12)
    dump_title_x = left_panel_x + section_padding_x
    dump_title_y = left_mid_y - 0.25 * inch
    c.drawString(dump_title_x, dump_title_y, "End-of-day Brain Dump")
    dump_line_spacing = 0.3 * inch
    first_dump_line_y = dump_title_y - 0.5 * inch
    c.setLineWidth(1)
    y = first_dump_line_y
    while y > left_panel_bottom + 0.25 * inch:
        c.line(
            left_panel_x + section_padding_x,
            y,
            left_panel_right_x - section_padding_x,
            y,
        )
        y -= dump_line_spacing

    # --- Right column: 30-minute schedule 8:00--16:00 ---
    right_panel_top = daily_top
    right_panel_bottom = daily_bottom
    right_panel_height = right_panel_top - right_panel_bottom
    c.setLineWidth(1.2)
    c.rect(
        right_panel_x,
        right_panel_bottom,
        right_panel_width,
        right_panel_height,
        stroke=1,
        fill=0,
    )
    slot_count = 16
    slot_height = right_panel_height / slot_count
    c.setFont("Helvetica", 9)
    for i in range(slot_count):
        row_top = right_panel_top - i * slot_height
        if i > 0:
            c.setLineWidth(0.8)
            c.line(right_panel_x, row_top, right_panel_right_x, row_top)
        total_minutes = 8 * 60 + 30 * i
        hour = total_minutes // 60
        minute = total_minutes % 60
        time_label = f"{hour}:{minute:02d}"
        label_x = right_panel_x + 0.1 * inch
        label_y = row_top - 0.3 * slot_height
        c.drawString(label_x, label_y, time_label)
    c.setLineWidth(1)


def export_to_pdf(path: str | Path) -> None:
    """
    Render a one-page blank daily planner template.

    Layout (all on a single letter page, portrait):
    - Top 1/10: Date label with underline for handwriting.
    - Next 2/10: Top 3 weekly priorities, numbered 1–3 with lines.
    - Last 7/10:
        - Left 2/3:
            - Top 1/2: Top 3 priorities for the day.
            - Bottom 1/2: End-of-day brain dump with handwriting lines.
        - Right ~1/3: 30-minute schedule from 8:00 to 16:00 (16 slots).
    """
    path = Path(path)
    c = canvas.Canvas(str(path), pagesize=letter)
    geom = _compute_geometry()
    _draw_date_band_single(c, geom)
    _draw_rest_of_page(c, geom)
    c.save()


def export_work_week_to_pdf(path: str | Path, start_date: date) -> None:
    """
    Render a 5-page work-week planner (start_date through start_date+4).
    Each page has the same layout as the daily planner; the date band shows
    the page date on the left and a 2-row table (M T W T F; 3/2 3/3 ...) on
    the right, with date cells linking to the corresponding page.
    """
    path = Path(path)
    c = canvas.Canvas(str(path), pagesize=letter)
    geom = _compute_geometry()
    dates = [start_date + timedelta(days=i) for i in range(5)]
    destination_names = [f"day_{i}" for i in range(5)]

    for i in range(5):
        c.bookmarkPage(destination_names[i])
        _draw_date_band_work_week(
            c, geom, dates[i], dates, destination_names, i
        )
        _draw_rest_of_page(c, geom)
        if i < 4:
            c.showPage()

    c.save()

