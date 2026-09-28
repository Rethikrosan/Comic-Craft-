import os
os.environ["IMAGE_BACKEND"] = "mock"

def run_smoke_test():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    assert client.get("/health").status_code == 200
    r = client.post("/generate-comic/json", json={
        "story_prompt": "A tiny robot learns to paint.",
        "character_name": "Robo",
        "setting": "A bright workshop",
        "tone": "Funny",
        "art_style": "Comic book",
    })
    assert r.status_code == 200, r.text
    assert len(r.json()["panels"]) == 5
    print("ComicCraft smoke test passed.")

def test_smoke():
    run_smoke_test()

if __name__ == "__main__":
    run_smoke_test()

