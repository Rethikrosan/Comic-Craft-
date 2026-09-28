from datetime import datetime
from pathlib import Path
from fpdf import FPDF
from app.config import get_settings
from app.models import ComicPanel

def _safe_text(text: str) -> str:
    return text.encode("latin-1", "replace").decode("latin-1")

def save_pdf(panels: list[ComicPanel], title: str) -> str:
    settings = get_settings()
    filename = f"comic-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.pdf"
    output = settings.export_dir / filename

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in panels:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(180, 12, _safe_text(f"Panel {panel.panel_number}: {panel.title}"), new_x="LMARGIN", new_y="NEXT", align="C")
        
        image_path = Path(panel.image_path)
        if image_path.exists():
            pdf.image(str(image_path), x=15, y=28, w=180, h=105)
            
        pdf.set_xy(15, 140)
        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(180, 7, _safe_text(panel.scene_description), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(180, 7, _safe_text("Caption:"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(180, 7, _safe_text(panel.caption), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(180, 7, _safe_text("Narration:"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(180, 7, _safe_text(panel.narration), new_x="LMARGIN", new_y="NEXT")
        
        if panel.dialogue:
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(180, 7, _safe_text("Dialogue:"), new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(180, 7, _safe_text(panel.dialogue), new_x="LMARGIN", new_y="NEXT")

    pdf.output(str(output))
    return str(output)

