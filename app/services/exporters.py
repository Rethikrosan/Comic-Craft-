from datetime import datetime
from pathlib import Path
import re

from fpdf import FPDF
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent.parent
EXPORTS_DIR = BASE_DIR / "static" / "exports"
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_filename(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower())
    return value.strip("-")[:50] or "comic"


class ComicPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "ComicCraft", ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _latin_safe(text: str) -> str:
    # Built-in Helvetica in FPDF has limited Unicode support.
    # Replace unsupported characters rather than crashing PDF export.
    return text.encode("latin-1", "replace").decode("latin-1")


def save_pdf(layout: list[dict], character_name: str) -> str:
    filename = (
        f"{_safe_filename(character_name)}-"
        f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.pdf"
    )
    path = EXPORTS_DIR / filename

    pdf = ComicPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 14)
        pdf.multi_cell(0, 8, _latin_safe(
            f"Panel {panel['panel_number']}: {panel['title']}"
        ))

        image_path = Path(panel["image_path"])
        if image_path.exists():
            with Image.open(image_path) as img:
                width, height = img.size
            max_w, max_h = 180, 105
            scale = min(max_w / width, max_h / height)
            display_w, display_h = width * scale, height * scale
            x = (210 - display_w) / 2
            pdf.image(str(image_path), x=x, y=30, w=display_w, h=display_h)
            pdf.set_y(30 + display_h + 7)

        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, _latin_safe(panel["scene_description"]))
        pdf.ln(2)

        if panel.get("caption"):
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, _latin_safe("Caption: " + panel["caption"]))

        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, _latin_safe(panel["narration"]))

        if panel.get("dialogue"):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 6, _latin_safe("Dialogue: " + panel["dialogue"]))

    pdf.output(str(path))
    return str(path)
