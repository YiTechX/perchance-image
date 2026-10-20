import os
import sys
import time
import base64
import io
import re
from typing import Optional, List, Dict, Any, Callable, Union
from PIL import Image

try:
    import perchancy
except ImportError:
    raise RuntimeError("perchancy package is not installed. Please install it with: pip install perchancy")


# Popular styles curated from Perchance's 79+ art styles
POPULAR_STYLES = [
    "Cinematic",
    "Casual Photo",
    "Painted Anime",
    "Digital Painting",
    "Concept Art",
    "3D Disney Character",
    "2D Disney Character",
    "Disney Sketch",
    "Oil Painting",
    "Watercolor",
    "Comic Book",
    "Cyberpunk",
    "Pixel Art",
    "Pencil Sketch",
    "Fantasy Art",
    "Dark Fantasy",
    "Vaporwave",
    "Vintage Photography",
    "Origami",
    "Claymation",
]

SHAPE_MAPPINGS = {
    # Square (1:1)
    "square": "768x768",
    "1:1": "768x768",
    "768x768": "768x768",
    # Portrait (vertical)
    "portrait": "512x768",
    "9:16": "512x768",
    "3:4": "512x768",
    "vertical": "512x768",
    "512x768": "512x768",
    # Landscape (horizontal)
    "landscape": "768x512",
    "16:9": "768x512",
    "4:3": "768x512",
    "horizontal": "768x512",
    "768x512": "768x512",
}


def normalize_shape(shape_input: Optional[str]) -> str:
    """Normalizes aspect ratio / shape input into Perchance resolution string (e.g., '768x768')."""
    if not shape_input:
        return "768x768"
    key = str(shape_input).strip().lower()
    return SHAPE_MAPPINGS.get(key, "768x768")


class PerchanceImageClient:
    """
    High-performance client for Perchance AI Text-to-Image Generator (https://perchance.org/ai-text-to-image-generator).
    Features:
      - 100% Free & Unlimited (Zero cookies or login required)
      - Cloudflare Turnstile bot evasion via DrissionPage
      - 79+ Art Styles & Aspect Ratio options
      - Persistent browser session reuse for lightning-fast multi-turn generation
    """

    def __init__(self, headless: bool = True, debug: bool = False):
        self.headless = headless
        self.debug = debug
        self._client: Optional[perchancy.Client] = None

    def _get_client(self) -> perchancy.Client:
        if self._client is None:
            self._client = perchancy.Client(headless=self.headless, debug=self.debug)
        return self._client

    def close(self) -> None:
        """Closes the underlying browser session and frees resources."""
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    def __enter__(self) -> "PerchanceImageClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def generate(
        self,
        prompt: str,
        style: Optional[str] = None,
        shape: str = "square",
        negative_prompt: Optional[str] = None,
        num_images: int = 1,
        disable_safety_settings: bool = True,
        output_dir: Optional[str] = None,
        output_file: Optional[str] = None,
        timeout: int = 90,
        on_status: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, Any]:
        """
        Generates one or more images using Perchance AI Text-to-Image Generator.

        Args:
            prompt: Text prompt describing the image.
            style: Art style (e.g. 'Cinematic', 'Casual Photo', 'Painted Anime', 'Digital Painting').
            shape: Aspect ratio ('square' [1:1], 'portrait' [9:16], 'landscape' [16:9]).
            negative_prompt: Optional things to avoid.
            num_images: Number of images to generate (default: 1).
            disable_safety_settings: If True, bypasses Perchance NSFW / content guard warning.
            output_dir: Directory where generated image(s) will be saved.
            output_file: Specific file path to save single generated image.
            timeout: Generation timeout in seconds (default: 90).
            on_status: Callback to receive status updates.

        Returns:
            Dict containing 'prompt', 'style', 'shape', 'saved_paths', 'images', and 'elapsed_time'.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        client = self._get_client()
        resolution = normalize_shape(shape)

        extra_params: Dict[str, Any] = {
            "shape": resolution,
        }

        # Apply style if specified
        if style and style.strip():
            clean_style = style.strip()
            # If user didn't prefix with ref:optionKeyName:, let perchancy match by text
            extra_params["style"] = clean_style

        # Incorporate negative prompt if provided
        final_prompt = prompt.strip()
        if negative_prompt and negative_prompt.strip():
            final_prompt = f"{final_prompt} [negative: {negative_prompt.strip()}]"

        if on_status:
            on_status("Connecting to Perchance and initializing generation...")

        start_time = time.time()

        try:
            res = client.images.generate(
                model="ai-text-to-image-generator",
                prompt=final_prompt,
                num_images=num_images,
                image_format="png",
                time_for_image=timeout,
                extra_params=extra_params,
                disable_safety_settings=disable_safety_settings,
            )
        except Exception as err:
            raise RuntimeError(f"Perchance generation failed: {err}") from err

        elapsed = time.time() - start_time

        if res.get("error"):
            raise RuntimeError(f"Perchance generation error: {res['error']}")

        data_items = res.get("data", [])
        if not data_items:
            raise RuntimeError("No image data returned from Perchance.")

        if on_status:
            on_status(f"Received {len(data_items)} image(s), processing and saving...")

        # Setup destination folder
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
        os.makedirs(output_dir, exist_ok=True)

        saved_paths: List[str] = []
        pil_images: List[Image.Image] = []

        timestamp = int(time.time())

        for idx, item in enumerate(data_items):
            raw_url = item.get("url", "")
            if not raw_url:
                continue

            # Strip data URI header if present
            if raw_url.startswith("data:"):
                raw_b64 = raw_url.split(",", 1)[1]
            else:
                raw_b64 = raw_url

            img_bytes = base64.b64decode(raw_b64)
            img = Image.open(io.BytesIO(img_bytes))
            pil_images.append(img)

            # Determine file path
            if output_file and len(data_items) == 1:
                target_path = output_file
            elif output_file:
                base, ext = os.path.splitext(output_file)
                target_path = f"{base}_{idx+1}{ext or '.png'}"
            else:
                slug = re.sub(r"[^a-zA-Z0-9_\-]+", "_", prompt.strip()[:30]).strip("_") or "image"
                target_path = os.path.join(output_dir, f"perchance_{slug}_{timestamp}_{idx+1}.png")

            os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
            img.save(target_path, format="PNG")
            saved_paths.append(target_path)

        return {
            "prompt": prompt,
            "style": style,
            "shape": resolution,
            "saved_paths": saved_paths,
            "images": pil_images,
            "elapsed_time": round(elapsed, 2),
        }
