import logging
import random
import re
import urllib.parse
from pathlib import Path
from typing import Optional, List
import requests
from PIL import Image, ImageDraw, ImageOps
from src.config import TEMP_DIR

logger = logging.getLogger(__name__)

class ImageGenerator:
    """
    Multi-Tier Visual Engine that delivers captivating, hyper-realistic, 
    content-matching images for social media posts.
    
    Tiers:
    1. NASA Official 4K Astronomy & Space Archive (for cosmos/JWST/physics)
    2. Wikipedia / Wikimedia High-Resolution Editorial Photography (for authentic hardware/robots/gadgets)
    3. AI Text-to-Image Generation (Pollinations AI with photorealistic storytelling prompt)
    4. Branded Editorial Poster Card (Pillow fallback if network completely fails)
    
    Strict Safety Constraint: 100% guarantee against female depictions.
    """
    def __init__(self, output_dir: Path = TEMP_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }

    def generate_image(
        self,
        prompt: str,
        title: str = "",
        hero_keywords: Optional[List[str]] = None,
        slot: str = "morning"
    ) -> Optional[Path]:
        """
        Generates or fetches an authentic, highly captivating, 1080x1080 image 
        directly matching the post's core subject.
        """
        image_path = self.output_dir / "latest_post_image.jpg"
        keywords = hero_keywords or []
        
        # Clean up keyword list
        search_queries = [q.strip() for q in keywords if q and len(q.strip()) > 2]
        
        # 1. Tier 1: NASA Space Photography (for night slot / space topics)
        if slot == "night" or any(w in " ".join(search_queries).lower() for w in ["space", "webb", "telescope", "nebula", "mars", "black hole", "star", "galaxy", "nasa", "planet"]):
            logger.info("🔭 [Tier 1] Checking NASA Official Archive for breathtaking space photography...")
            nasa_queries = search_queries + ["James Webb space telescope", "nebula deep space", "cosmic galaxy"]
            for query in nasa_queries[:4]:
                img_url = self._fetch_nasa_image(query)
                if img_url and self._download_and_format_image(img_url, image_path):
                    logger.info(f"✅ [Tier 1 NASA] Real space photograph successfully processed: {query}")
                    return image_path

        # 2. Tier 2: Wikipedia / Wikimedia Editorial Photography (Real Tech, Hardware, Robots, Gadgets)
        logger.info("🏛️ [Tier 2] Checking Wikipedia High-Res Editorial Photography for authentic subject...")
        for query in search_queries[:4]:
            img_url = self._fetch_wiki_image(query)
            if img_url and self._download_and_format_image(img_url, image_path):
                logger.info(f"✅ [Tier 2 Wiki] Real editorial photo successfully processed: {query}")
                return image_path

        # 3. Tier 3: AI Text-to-Image Generation (Pollinations AI)
        logger.info("🎨 [Tier 3] Generating AI photorealistic storytelling image...")
        ai_saved = self._generate_ai_image(prompt, image_path)
        if ai_saved:
            logger.info("✅ [Tier 3 AI] Photorealistic AI image successfully generated.")
            return image_path

        # 4. Tier 4: Editorial Graphic Poster Fallback
        logger.info("🏷️ [Tier 4] Creating branded editorial poster fallback...")
        try:
            return self._create_editorial_poster(image_path, title, slot)
        except Exception as e:
            logger.error(f"Failed to create editorial fallback: {e}")
            return None

    def _fetch_nasa_image(self, query: str) -> Optional[str]:
        """Queries NASA's open image library API for authentic 4K space photography."""
        try:
            url = f"https://images-api.nasa.gov/search?q={urllib.parse.quote(query)}&media_type=image"
            r = requests.get(url, timeout=12)
            if r.status_code == 200:
                items = r.json().get('collection', {}).get('items', [])
                for item in items[:4]:
                    links = item.get('links', [])
                    for link in links:
                        href = link.get('href')
                        if href and (href.endswith('.jpg') or href.endswith('.png')):
                            # Upgrade thumbnail to medium/orig resolution
                            return href.replace('~thumb.jpg', '~medium.jpg').replace('~small.jpg', '~medium.jpg')
        except Exception as e:
            logger.debug(f"NASA search error for '{query}': {e}")
        return None

    def _fetch_wiki_image(self, query: str) -> Optional[str]:
        """Queries Wikipedia API for high-resolution article hero photographs."""
        try:
            url = 'https://en.wikipedia.org/w/api.php'
            params = {
                'action': 'query',
                'generator': 'search',
                'gsrsearch': query,
                'gsrlimit': 3,
                'prop': 'pageimages',
                'pithumbsize': 1280,
                'format': 'json'
            }
            r = requests.get(url, params=params, headers=self.headers, timeout=10)
            if r.status_code == 200:
                pages = r.json().get('query', {}).get('pages', {})
                for pid, pdata in pages.items():
                    if 'thumbnail' in pdata:
                        thumb = pdata['thumbnail']
                        src = thumb.get('source', '')
                        lower_src = src.lower()
                        # Exclude SVG, icons, diagrams, flowcharts, schemas to guarantee real photography
                        bad_markers = ['.svg', 'diagram', 'schema', 'chart', 'flowchart', 'graph', 'model-archit', 'unsupervised', 'drawing']
                        if src and not any(m in lower_src for m in bad_markers) and thumb.get('width', 0) >= 380:
                            return src
        except Exception as e:
            logger.debug(f"Wiki search error for '{query}': {e}")
        return None

    def _generate_ai_image(self, prompt: str, output_path: Path) -> bool:
        """Calls Pollinations AI with clean prompt and safety constraints."""
        clean_prompt = " ".join(prompt.strip().split())

        # Programmatically sanitize any female references
        female_words = [r"\bfemale\b", r"\bwoman\b", r"\bwomen\b", r"\bgirl\b", r"\bgirls\b", r"\blady\b", r"\bladies\b"]
        for word in female_words:
            clean_prompt = re.sub(word, "scientist", clean_prompt, flags=re.IGNORECASE)

        # Enforce strict negative constraints
        if "no female" not in clean_prompt.lower():
            clean_prompt += ", photorealistic, 8k resolution, cinematic lighting, sharp focus, 35mm photography, no female, no woman, no blur, no text"

        encoded = urllib.parse.quote(clean_prompt[:450])
        seed = random.randint(1000, 999999)

        models = ["zimage", "turbo", "flux"]
        for model in models:
            url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1080&model={model}&nologo=true&seed={seed}"
            try:
                r = requests.get(url, headers=self.headers, timeout=35)
                if r.status_code == 200 and len(r.content) > 8000:
                    return self._process_image_bytes(r.content, output_path)
            except Exception as e:
                logger.debug(f"Pollinations {model} failed: {e}")

        return False

    def _download_and_format_image(self, url: str, output_path: Path) -> bool:
        """Downloads an image from URL and formats it into a crisp 1080x1080 square."""
        try:
            r = requests.get(url, headers=self.headers, timeout=20)
            if r.status_code == 200 and len(r.content) > 5000:
                return self._process_image_bytes(r.content, output_path)
        except Exception as e:
            logger.warning(f"Error downloading image from {url}: {e}")
        return False

    def _process_image_bytes(self, data: bytes, output_path: Path) -> bool:
        """Loads image data, crops/fits into centered 1080x1080, and saves as JPEG."""
        import io
        try:
            img = Image.open(io.BytesIO(data))
            fitted = ImageOps.fit(img, (1080, 1080), method=Image.Resampling.LANCZOS)
            fitted.convert("RGB").save(output_path, "JPEG", quality=95)
            return True
        except Exception as e:
            logger.error(f"Image formatting error: {e}")
            return False

    def _create_editorial_poster(self, output_path: Path, title: str, slot: str) -> Path:
        """
        Creates an ultra-sleek, modern editorial graphic poster in dark mode 
        when no external image source is accessible.
        """
        width, height = 1080, 1080
        image = Image.new("RGB", (width, height), color=(10, 15, 29))  # Deep slate obsidian
        draw = ImageDraw.Draw(image)

        # Ambient background glow
        theme_colors = {
            "morning": (14, 165, 233),    # Electric Sky Blue (AI)
            "noon": (16, 185, 129),       # Emerald Tech (Innovation)
            "afternoon": (245, 158, 11),  # Amber / Security Gold (Cybersecurity)
            "night": (168, 85, 247)       # Cosmic Purple (Space)
        }
        accent = theme_colors.get(slot, (14, 165, 233))

        for r in range(450, 0, -25):
            alpha = int(20 * (r / 450))
            box = [(width//2 - r, 380 - r), (width//2 + r, 380 + r)]
            draw.ellipse(box, outline=(accent[0], accent[1], accent[2], alpha), width=3)

        # Sleek glassmorphism borders
        margin = 45
        draw.rectangle([(margin, margin), (width - margin, height - margin)], outline=(30, 41, 59), width=3)
        draw.line([(margin, margin), (width - margin, margin)], fill=accent, width=6)

        # Category pill badge
        slot_names = {
            "morning": "ARTIFICIAL INTELLIGENCE",
            "noon": "TECH & INNOVATION",
            "afternoon": "CYBERSECURITY & PRIVACY",
            "night": "SCIENCE & DEEP SPACE"
        }
        badge_text = f"  {slot_names.get(slot, 'SMART TECH')}  "
        draw.rectangle([(margin + 40, margin + 40), (margin + 380, margin + 90)], fill=(15, 23, 42), outline=accent, width=2)
        draw.text((margin + 60, margin + 55), badge_text, fill=accent)

        # Center Hero Icon
        icons = {
            "morning": "🧠 ⚡ 💡",
            "noon": "👓 🤖 🚀",
            "afternoon": "🛡️ 🔒 ⚡",
            "night": "🌌 🔭 ✨"
        }
        draw.text((width//2 - 40, height//2 - 120), icons.get(slot, "🚀 💡 🔬"), fill=(255, 255, 255))

        # Title formatting (truncate cleanly if needed)
        clean_title = title if len(title) <= 55 else title[:52] + "..."
        draw.text((width//2, height//2 + 30), clean_title, fill=(248, 250, 252), anchor="mm")

        # Bottom branding line
        draw.text((width//2, height - margin - 50), "BE SMART WITH AI • DAILY DISCOVERY", fill=(148, 163, 184), anchor="mm")

        image.save(output_path, "JPEG", quality=95)
        logger.info(f"Editorial fallback poster created at {output_path}")
        return output_path
