import httpx
import re
import pathlib
from PIL import Image

story_prompt = "A young explorer enters an ancient temple hidden deep inside a jungle. Inside the temple, she discovers a glowing golden crystal. Suddenly, the temple begins to collapse and she runs toward the exit carrying the crystal."

res = httpx.post("http://127.0.0.1:8000/generate", data={
    "story_prompt": story_prompt,
    "character_name": "Lyra",
    "setting": "Ancient jungle temple",
    "tone": "Adventurous",
    "art_style": "Comic book"
})
print("HTTP POST /generate STATUS:", res.status_code)
html = res.text
assert "YOUR COMIC" in html

img_urls = re.findall(r'src="(/static/panels/[^"]+)"', html)
print(f"FOUND {len(img_urls)} PANEL IMAGE URLS IN HTML:")

for i, url in enumerate(img_urls, 1):
    img_res = httpx.get(f"http://127.0.0.1:8000{url}")
    print(f"\n[Panel {i}] URL: {url}")
    print(f"  HTTP GET Status: {img_res.status_code}, Content-Type: {img_res.headers.get('content-type')}, Size: {len(img_res.content)} bytes")
    assert img_res.status_code == 200
    assert "image/png" in img_res.headers.get("content-type", "")
    
    filename = url.split("/")[-1]
    file_path = pathlib.Path("static/panels") / filename
    assert file_path.exists()
    assert file_path.stat().st_size > 0
    
    img = Image.open(file_path)
    print(f"  Pillow Verification: Dimensions={img.size}, Format={img.format}, Mode={img.mode}")
    assert img.size == (768, 768)

print("\nPIPELINE VERIFICATION FOR USER'S STORY COMPLETED WITH 100% SUCCESS!")
