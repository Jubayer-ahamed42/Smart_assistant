import logging
import random
import urllib.parse
from pathlib import Path
from typing import Optional
import requests
from PIL import Image, ImageDraw
from src.config import TEMP_DIR

logger = logging.getLogger(__name__)

class ImageGenerator:
    def __init__(self, output_dir: Path = TEMP_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

    def generate_image(self, prompt: str, title: str = "") -> Optional[Path]:
        """
        Generates an AI image based on the prompt using Pollinations AI (Flux model).
        If network fails, creates a high-res graphic card using Pillow as fallback.
        Returns the absolute Path of the saved image file, or None.
        """
        image_path = self.output_dir / "latest_post_image.jpg"

        # Attempt 1: Pollinations.ai with Flux model
        # Clean prompt for URL
        clean_prompt = prompt.strip().replace("\n", " ")
        encoded_prompt = urllib.parse.quote(clean_prompt)
        seed = random.randint(1000, 999999)

        models = ["flux", "turbo"]
        for model in models:
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1080&model={model}&nologo=true&seed={seed}"
            logger.info(f"Generating AI image via Pollinations ({model} model)...")
            try:
                response = requests.get(url, timeout=50)
                if response.status_code == 200 and len(response.content) > 5000:
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"AI image successfully generated and saved: {image_path} ({len(response.content)} bytes)")
                    return image_path
                else:
                    logger.warning(f"Pollinations {model} returned status {response.status_code}. Retrying...")
            except Exception as e:
                logger.warning(f"Pollinations {model} request failed: {e}. Trying fallback...")

        # Attempt 2: Fallback to Pillow high-quality gradient card
        logger.info("Generating fallback branded graphic with Pillow...")
        try:
            return self._create_fallback_banner(image_path, title)
        except Exception as e:
            logger.error(f"Failed to create fallback graphic: {e}")
            return None

    def _create_fallback_banner(self, output_path: Path, title: str) -> Path:
        """
        Creates an aesthetic dark-mode gradient graphic card when AI image generation is unavailable.
        """
        width, height = 1080, 1080
        image = Image.new("RGB", (width, height), color=(15, 23, 42))  # Slate dark
        draw = ImageDraw.Draw(image)

        # Draw tech decorative circles and glowing gradients
        for i in range(12):
            radius = 150 + i * 40
            alpha_color = (20 + i * 8, 30 + i * 12, 60 + i * 15)
            draw.ellipse(
                [(width // 2 - radius, height // 2 - radius), (width // 2 + radius, height // 2 + radius)],
                outline=alpha_color,
                width=2
            )

        # Draw decorative frame
        margin = 40
        draw.rectangle(
            [(margin, margin), (width - margin, height - margin)],
            outline=(59, 130, 246),  # Electric blue
            width=4
        )

        image.save(output_path, "JPEG", quality=90)
        logger.info(f"Fallback graphic created at {output_path}")
        return output_path
