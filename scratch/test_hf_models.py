import sys
sys.path.insert(0, ".")

from app.config import get_settings
from huggingface_hub import InferenceClient

settings = get_settings()

models_to_test = [
    "black-forest-labs/FLUX.1-schnell",
    "black-forest-labs/FLUX.1-dev",
    "stabilityai/stable-diffusion-3.5-large",
    "runwayml/stable-diffusion-v1-5",
    "prompthero/openjourney",
    "stabilityai/stable-diffusion-xl-base-1.0"
]

for m in models_to_test:
    print(f"\n--- Testing model: {m} ---")
    try:
        client = InferenceClient(api_key=settings.hf_api_key)
        image = client.text_to_image(
            "A young explorer entering an ancient jungle temple, comic book style",
            model=m,
        )
        safe_m = m.replace("/", "_")
        out_path = f"static/panels/test_hf_{safe_m}.png"
        image.save(out_path)
        print(f"SUCCESS! Model {m} generated real image saved to {out_path}")
        print("Image details:", image.size, image.format)
        break
    except Exception as exc:
        print(f"FAILED {m}: {type(exc).__name__} - {exc}")
