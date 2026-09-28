import os
import httpx
import pathlib
from PIL import Image

story_prompt = "A young explorer named Lyra enters an ancient temple hidden deep inside a jungle. She discovers a mysterious glowing golden crystal inside the temple. When she touches it, the temple begins to collapse. Lyra grabs the crystal and runs toward the exit while huge stone pillars fall around her. She escapes the temple and stands outside holding the glowing crystal as sunlight shines through the jungle."

print("=== STARTING REAL AI COMIC GENERATION TEST ===")
print("Sending request to FastAPI backend...")

try:
    res = httpx.post("http://127.0.0.1:8000/generate-comic/json", json={
        "story_prompt": story_prompt,
        "character_name": "Lyra",
        "setting": "Ancient jungle temple",
        "tone": "Adventurous",
        "art_style": "Comic book"
    }, timeout=120.0)

    print("HTTP STATUS:", res.status_code)
    if res.status_code != 200:
        print("ERROR RESPONSE:", res.text)
    else:
        data = res.json()
        print("Comic ID:", data.get("comic_id"))
        print("Title:", data.get("title"))
        print("PDF URL:", data.get("pdf_url"))
        panels = data.get("panels", [])
        print(f"Total Panels Generated: {len(panels)}")

        for p in panels:
            print(f"\n--- Panel {p['panel_number']}: {p['title']} ---")
            print("Scene Description:", p["scene_description"])
            print("Image Prompt:", p["image_prompt"])
            print("Image URL:", p["image_url"])
            print("Image Path:", p["image_path"])

            img_path = pathlib.Path(p["image_path"])
            if img_path.exists():
                size = img_path.stat().st_size
                print(f"File Size: {size} bytes")
                img = Image.open(img_path)
                print(f"PIL Image Info: Format={img.format}, Size={img.size}, Mode={img.mode}")
            else:
                print("FILE DOES NOT EXIST!")

            # Check HTTP URL
            img_res = httpx.get(f"http://127.0.0.1:8000{p['image_url']}")
            print(f"Browser HTTP GET Status: {img_res.status_code}, Content-Type: {img_res.headers.get('content-type')}")

        # Check PDF download
        pdf_res = httpx.get(f"http://127.0.0.1:8000{data['pdf_url']}")
        print(f"\nPDF Download HTTP Status: {pdf_res.status_code}, Content-Type: {pdf_res.headers.get('content-type')}, Size: {len(pdf_res.content)} bytes")

except Exception as exc:
    print("EXCEPTION OCCURRED:", type(exc).__name__, exc)
