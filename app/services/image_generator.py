import base64
import io
import re
import threading
from pathlib import Path
from typing import Optional

import requests
from PIL import Image

from app.config import settings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PANELS_DIR = BASE_DIR / "static" / "panels"
PANELS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_filename(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower())
    return value.strip("-")[:60] or "panel"


class ImageGenerator:
    def __init__(self):
        self._pipeline = None
        self._lock = threading.Lock()

    def _device(self) -> str:
        if settings.image_device != "auto":
            return settings.image_device
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    def _load_pipeline(self):
        if self._pipeline is not None:
            return self._pipeline

        with self._lock:
            if self._pipeline is not None:
                return self._pipeline

            try:
                import torch
                from diffusers import StableDiffusionPipeline
            except ImportError as exc:
                raise RuntimeError(
                    "Local image generation requires torch and diffusers. "
                    "Run: pip install -r requirements.txt"
                ) from exc

            device = self._device()
            dtype = torch.float16 if device == "cuda" else torch.float32

            self._pipeline = StableDiffusionPipeline.from_pretrained(
                settings.image_model,
                torch_dtype=dtype,
            )
            self._pipeline = self._pipeline.to(device)

            if device == "cuda":
                self._pipeline.enable_attention_slicing()

        return self._pipeline

    def _generate_local(self, prompt: str) -> Image.Image:
        pipe = self._load_pipeline()
        result = pipe(
            prompt=prompt,
            negative_prompt=(
                "blurry, low quality, distorted face, extra fingers, malformed hands, "
                "duplicate character, text, watermark, logo"
            ),
            width=settings.image_width,
            height=settings.image_height,
            num_inference_steps=settings.image_steps,
            guidance_scale=settings.image_guidance_scale,
        )
        return result.images[0]

    def _generate_hf(self, prompt: str) -> Image.Image:
        if not settings.hf_api_key:
            raise RuntimeError(
                "HF_API_KEY is required when IMAGE_BACKEND=hf."
            )

        url = f"https://api-inference.huggingface.co/models/{settings.image_model}"
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {settings.hf_api_key}"},
            json={"inputs": prompt},
            timeout=180,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Hugging Face image generation failed ({response.status_code}): "
                f"{response.text[:500]}"
            )
        return Image.open(io.BytesIO(response.content)).convert("RGB")

    def generate(self, prompt: str, filename_hint: str = "panel") -> str:
        enhanced = (
            "Professional sequential comic illustration, cohesive character design, "
            "clear focal subject, cinematic composition, expressive faces, detailed "
            "environment, clean linework, rich colors, print-ready quality. "
            + prompt
        )

        if settings.image_backend.lower() == "hf":
            image = self._generate_hf(enhanced)
        elif settings.image_backend.lower() == "diffusers":
            image = self._generate_local(enhanced)
        else:
            raise RuntimeError(
                "IMAGE_BACKEND must be either 'diffusers' or 'hf'."
            )

        filename = f"{_safe_filename(filename_hint)}.png"
        path = PANELS_DIR / filename
        image.save(path, format="PNG")
        return str(path)

    def clear(self):
        self._pipeline = None


image_generator = ImageGenerator()
