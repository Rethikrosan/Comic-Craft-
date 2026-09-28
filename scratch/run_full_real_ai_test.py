import sys
sys.path.insert(0, ".")

import httpx
import pathlib
from PIL import Image

story_prompt = "A young explorer named Lyra enters an ancient temple hidden deep inside a jungle. She discovers a mysterious glowing golden crystal inside the temple. When she touches it, the temple begins to collapse. Lyra grabs the crystal and runs toward the exit while huge stone pillars fall around her. She escapes the temple and stands outside holding the glowing crystal as sunlight shines through the jungle."

print("=== STARTING COMPLETE REAL AI GENERATION VERIFICATION ===")
print("Posting story request to FastAPI app...")

res = httpx.post("http://127.0.0.1:8000/generate-comic/json", json={
    "story_prompt": story_prompt,
    "character_name": "Lyra",
    "setting": "Ancient jungle temple",
    "tone": "Adventurous",
    "art_style": "Comic book"
}, timeout=180.0)

print("HTTP STATUS:", res.status_code)
if res.status_code != 200:
    print("ERROR RESPONSE:", res.text)
    sys.exit(1)

data = res.json()
print("\nComic ID:", data.get("comic_id"))
print("Title:", data.get("title"))
print("PDF URL:", data.get("pdf_url"))

panels = data.get("panels", [])
print(f"\nTotal Panels Generated: {len(panels)}")

for p in panels:
    num = p['panel_number']
    print(f"\n==================== PANEL {num}: {p['title']} ====================")
    print("Scene Description:", p["scene_description"])
    print("Image Prompt:", p["image_prompt"])
    print("Image URL:", p["image_url"])
    print("Image Path:", p["image_path"])

    img_path = pathlib.Path(p["image_path"])
    assert img_path.exists(), f"Image file {img_path} does not exist"
    size = img_path.stat().st_size
    print(f"File Size: {size} bytes")
    assert size > 0, "Image file is empty"

    img = Image.open(img_path)
    print(f"Pillow Image Info: Format={img.format}, Dimensions={img.size}, Mode={img.mode}")
    assert img.size == (768, 768)

    # Test HTTP Browser static serving
    img_res = httpx.get(f"http://127.0.0.1:8000{p['image_url']}")
    print(f"Browser HTTP GET Status: {img_res.status_code}, Content-Type: {img_res.headers.get('content-type')}")
    assert img_res.status_code == 200
    assert "image/png" in img_res.headers.get("content-type", "")

# Verify PDF Export
pdf_url = data.get("pdf_url")
pdf_res = httpx.get(f"http://127.0.0.1:8000{pdf_url}")
print(f"\nPDF Export HTTP Status: {pdf_res.status_code}, Content-Type: {pdf_res.headers.get('content-type')}, Size: {len(pdf_res.content)} bytes")
assert pdf_res.status_code == 200
assert pdf_res.headers.get("content-type") == "application/pdf"
assert len(pdf_res.content) > 1000

print("\n=== COMPLETE REAL AI VERIFICATION SUCCESSFUL! ===")
