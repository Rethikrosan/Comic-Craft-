import uuid
from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models import PromptRequest
from app.ai.gemini_flash import generate_outline
from app.ai.gemini_pro import generate_story
from app.ai.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

router = APIRouter()
templates = Jinja2Templates(directory="templates")
COMICS = {}

def create_comic(data: PromptRequest):
    outlines = generate_outline(data.story_prompt, data.character_name, data.setting, data.tone, data.art_style)
    stories = generate_story(outlines, data.character_name, data.tone)
    image_paths = [generate_image(outline.image_prompt, outline.panel_number) for outline in outlines]
    layout = build_comic_layout(outlines, stories, image_paths)
    title = f"{data.character_name}'s Comic Adventure"
    pdf_path = save_pdf(layout, title)
    comic_id = uuid.uuid4().hex
    result = {
        "comic_id": comic_id,
        "title": title,
        "panels": [p.model_dump() for p in layout],
        "pdf_url": f"/export/{comic_id}",
    }
    COMICS[comic_id] = {"result": result, "pdf_path": pdf_path}
    return result

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@router.post("/generate", response_class=HTMLResponse)
async def generate_form(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        result = create_comic(data)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context=result
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=500
        )

@router.post("/generate-comic/json")
async def generate_json(payload: PromptRequest):
    try:
        return create_comic(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/export/{comic_id}")
async def export_comic(comic_id: str):
    comic = COMICS.get(comic_id)
    if not comic:
        raise HTTPException(status_code=404, detail="Comic not found. Generate it again.")
    path = Path(comic["pdf_path"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF file no longer exists.")
    return FileResponse(path, media_type="application/pdf", filename=path.name)

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={}
    )

@router.post("/test-image")
async def test_image(payload: dict):
    prompt = str(payload.get("prompt", "")).strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")
    try:
        path = generate_image(prompt, 0)
        return {"image_url": "/static/panels/" + Path(path).name}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/health")
async def health():
    return {"status": "ok", "service": "ComicCraft"}

