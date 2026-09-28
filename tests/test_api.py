import os
os.environ["IMAGE_BACKEND"] = "mock"
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ComicCraft"

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "ComicCraft" in response.text
    assert "Turn an idea into a comic" in response.text

def test_docs():
    response = client.get("/docs")
    assert response.status_code == 200

def test_test_image_endpoint():
    # Valid prompt
    response = client.post("/test-image", json={"prompt": "A heroic astronaut"})
    assert response.status_code == 200
    assert response.json()["image_url"].startswith("/static/panels/")

    # Missing prompt
    response_invalid = client.post("/test-image", json={"prompt": ""})
    assert response_invalid.status_code == 400

def test_json_generation_mock_mode():
    response = client.post("/generate-comic/json", json={
        "story_prompt": "A fox discovers a secret doorway in an ancient forest.",
        "character_name": "Finn",
        "setting": "Enchanted forest",
        "tone": "Funny",
        "art_style": "Comic book"
    })
    assert response.status_code == 200, response.text
    data = response.json()
    assert "comic_id" in data
    assert len(data["panels"]) == 5
    assert data["pdf_url"].startswith("/export/")

    # Verify PDF download route works for generated comic
    pdf_response = client.get(data["pdf_url"])
    assert pdf_response.status_code == 200
    assert pdf_response.headers["content-type"] == "application/pdf"

def test_form_generation_mock_mode():
    response = client.post("/generate", data={
        "story_prompt": "A dragon opens a cozy tea shop.",
        "character_name": "Ignis",
        "setting": "Ancient kingdom",
        "tone": "Light-hearted",
        "art_style": "Watercolor graphic novel"
    })
    assert response.status_code == 200
    assert "YOUR COMIC" in response.text
    assert "Ignis&#39;s Comic Adventure" in response.text or "Ignis's Comic Adventure" in response.text

def test_export_success_page():
    response = client.get("/export-success")
    assert response.status_code == 200
    assert "Your comic is ready!" in response.text

def test_export_not_found():
    response = client.get("/export/nonexistent-id-12345")
    assert response.status_code == 404
    assert response.json()["detail"] == "Comic not found. Generate it again."

def test_invalid_input_validation():
    # Story prompt too short (less than 3 chars)
    response = client.post("/generate-comic/json", json={
        "story_prompt": "Hi",
        "character_name": "Finn",
        "setting": "Forest",
        "tone": "Funny",
        "art_style": "Comic"
    })
    assert response.status_code == 422

def test_image_generation_and_static_serving_pipeline():
    from pathlib import Path
    from PIL import Image
    from app.ai.image_generator import generate_image

    # 1. Mock image generation returns a path
    image_prompt = "A heroic knight standing on a cliff at sunset"
    path_str = generate_image(image_prompt, 1)
    assert path_str, "Image generator should return a non-empty path"

    # 2. The file exists
    image_path = Path(path_str)
    assert image_path.exists(), f"File {image_path} does not exist on disk"

    # 3. File size is greater than zero
    size = image_path.stat().st_size
    assert size > 0, f"File {image_path} is empty (0 bytes)"

    # 4. Pillow can open the image
    img = Image.open(image_path)
    assert img is not None

    # 5. Image dimensions are valid (768x768)
    assert img.size == (768, 768)
    assert img.format == "PNG"

    # 6. /static/... URL returns HTTP 200
    rel_url = f"/static/panels/{image_path.name}"
    response = client.get(rel_url)
    assert response.status_code == 200, f"Failed to fetch static image at {rel_url}"

    # 7. Response content type is an image
    assert "image" in response.headers.get("content-type", "").lower()

def test_comic_generation_panels_and_pdf_images():
    from pathlib import Path
    from PIL import Image

    # 8. Comic generation returns image URLs & 9. Every generated panel has an image
    res = client.post("/generate-comic/json", json={
        "story_prompt": "A young wizard discovers a magical floating compass.",
        "character_name": "Elian",
        "setting": "Ancient observatory",
        "tone": "Adventurous",
        "art_style": "Anime"
    })
    assert res.status_code == 200
    data = res.json()
    panels = data.get("panels", [])
    assert len(panels) == 5

    for p in panels:
        assert "image_url" in p and p["image_url"].startswith("/static/panels/")
        assert "image_path" in p
        p_path = Path(p["image_path"])
        
        # Verify physical file existence, size, and loadability
        assert p_path.exists()
        assert p_path.stat().st_size > 0
        img = Image.open(p_path)
        assert img.size == (768, 768)

        # Verify browser HTTP URL serving
        img_res = client.get(p["image_url"])
        assert img_res.status_code == 200
        assert "image" in img_res.headers.get("content-type", "").lower()

    # 10. PDF export contains the generated images
    pdf_url = data.get("pdf_url")
    assert pdf_url
    pdf_res = client.get(pdf_url)
    assert pdf_res.status_code == 200
    assert pdf_res.headers.get("content-type") == "application/pdf"
    assert len(pdf_res.content) > 1000


