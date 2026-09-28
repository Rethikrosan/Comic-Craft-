# ComicCraft — AI Comic Story Creator

A complete FastAPI/Jinja2 application that turns a user prompt into a five-panel comic, generates illustrations, previews the result in the browser, and exports a multi-page PDF.

## Architecture

1. FastAPI receives the story prompt and preferences.
2. `app/ai/gemini_flash.py` creates the structured five-panel outline.
3. `app/ai/gemini_pro.py` expands each panel into narration, captions, and dialogue.
4. `app/ai/image_generator.py` creates one illustration per panel through Hugging Face Inference.
5. `app/layout_builder.py` combines text and images.
6. `app/exporters.py` creates the downloadable PDF.
7. Jinja2 templates render the home page, comic preview, and export confirmation.

## Model/backend compatibility

The supplied project specification names Gemini 1.5 Flash/Pro and local Stable Diffusion 1.5. This implementation preserves the requested pipeline while making model IDs configurable through `.env` and using Hugging Face Inference for image generation. It intentionally does not import local PyTorch/Diffusers.

`IMAGE_BACKEND=mock` generates placeholder images with Pillow so the entire workflow, including PDF export, can be tested without API keys or a GPU.

## Windows setup

Recommended Python: 3.11 or 3.12.

```powershell
cd ComicCraft
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

For the first smoke test, set `IMAGE_BACKEND=mock` in `.env`, then:

```powershell
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`

API docs: `http://127.0.0.1:8000/docs`

Health: `http://127.0.0.1:8000/health`

## Real AI mode

Put the required keys in `.env`:

```text
GEMINI_API_KEY=your_key
HF_API_KEY=your_huggingface_token
IMAGE_BACKEND=hf
```

Model IDs are configurable. Do not commit `.env`.

## API

`POST /generate` — browser form generation.

`POST /generate-comic/json` — JSON API.

Example:

```json
{
  "story_prompt": "A brave fox explores an enchanted forest.",
  "character_name": "Finn",
  "setting": "Enchanted forest",
  "tone": "Adventurous",
  "art_style": "Comic book"
}
```

`POST /test-image` accepts `{"prompt":"..."}`.

`GET /health` checks the service.

`GET /docs` opens FastAPI's interactive API documentation.

## Tests

```powershell
$env:IMAGE_BACKEND="mock"
pytest -q
```

Or:

```powershell
python smoke_test.py
```

## Project structure

```text
ComicCraft/
├── app/
│   ├── ai/
│   │   ├── gemini_flash.py
│   │   ├── gemini_pro.py
│   │   └── image_generator.py
│   ├── config.py
│   ├── exporters.py
│   ├── layout_builder.py
│   ├── main.py
│   ├── models.py
│   └── routes.py
├── static/
│   ├── css/style.css
│   ├── js/app.js
│   ├── panels/
│   └── exports/
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── tests/test_api.py
├── .env.example
├── .gitignore
├── requirements.txt
├── run_windows.bat
├── smoke_test.py
└── README.md
```
