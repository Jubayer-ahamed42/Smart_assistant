import base64
import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional
from src.config import TEMP_DIR

logger = logging.getLogger(__name__)

# Color themes matching our 4 daily slots
SLOT_THEMES = {
    "morning": {
        "badge_border": "rgba(56, 189, 248, 0.65)",
        "badge_bg": "rgba(14, 165, 233, 0.22)",
        "badge_color": "#38bdf8",
        "avatar_border": "#38bdf8",
        "avatar_glow": "rgba(56, 189, 248, 0.6)",
        "brand_border": "rgba(56, 189, 248, 0.4)",
        "default_category": "Artificial Intelligence",
        "icon": "🤖"
    },
    "noon": {
        "badge_border": "rgba(52, 211, 153, 0.65)",
        "badge_bg": "rgba(16, 185, 129, 0.22)",
        "badge_color": "#34d399",
        "avatar_border": "#34d399",
        "avatar_glow": "rgba(52, 211, 153, 0.6)",
        "brand_border": "rgba(52, 211, 153, 0.4)",
        "default_category": "Tech & Innovation",
        "icon": "⚡"
    },
    "afternoon": {
        "badge_border": "rgba(251, 191, 36, 0.65)",
        "badge_bg": "rgba(245, 158, 11, 0.22)",
        "badge_color": "#fbbf24",
        "avatar_border": "#fbbf24",
        "avatar_glow": "rgba(251, 191, 36, 0.6)",
        "brand_border": "rgba(251, 191, 36, 0.4)",
        "default_category": "Cybersecurity & Privacy",
        "icon": "🛡️"
    },
    "night": {
        "badge_border": "rgba(192, 132, 252, 0.65)",
        "badge_bg": "rgba(168, 85, 247, 0.22)",
        "badge_color": "#c084fc",
        "avatar_border": "#c084fc",
        "avatar_glow": "rgba(192, 132, 252, 0.6)",
        "brand_border": "rgba(192, 132, 252, 0.4)",
        "default_category": "Science & Deep Space",
        "icon": "🌌"
    }
}

class PhotoCardRenderer:
    """
    Renders editorial-quality Bengali Photo Cards (ফটোকার্ড) matching the style
    of leading tech & science media outlets (e.g., BigyanPriyo, Wired, BBC).
    
    Features:
    - Flawless Bengali OpenType text shaping (HarfBuzz/Chromium engine).
    - Cinematic gradient dark overlay for maximum text legibility.
    - Two-tone punchy typography (White + Golden Yellow highlight).
    - Category pill badge & page branding.
    - 1080x1080 Instagram/Facebook square resolution.
    - Offline self-contained Bengali font embedding (base64).
    """

    def __init__(self, font_path: Optional[Path] = None, avatar_path: Optional[Path] = None):
        self.font_path = font_path or Path("assets/fonts/HindSiliguri-Bold.ttf")
        self.avatar_path = avatar_path or Path("assets/page_profile_pic.png")
        self._font_b64 = None
        self._avatar_b64 = None
        self.browser_bin = self._locate_browser()
        if self.browser_bin:
            logger.info(f"📸 Headless browser located for PhotoCard rendering: {self.browser_bin}")
        else:
            logger.warning("⚠️ No headless browser found. PhotoCards will fall back to raw images.")

    def _locate_browser(self) -> Optional[str]:
        """Finds Chrome, Chromium, or Edge binary on Windows or Linux."""
        # 1. Check system PATH
        for name in ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "msedge"]:
            found = shutil.which(name)
            if found:
                return found

        # 2. Check standard Windows paths
        win_candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        for path in win_candidates:
            if os.path.exists(path):
                return path

        # 3. Check standard Linux / GitHub Actions runner paths
        linux_candidates = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser"
        ]
        for path in linux_candidates:
            if os.path.exists(path):
                return path

        return None

    def _get_font_b64(self) -> str:
        """Returns base64 encoded font for self-contained HTML embedding."""
        if self._font_b64 is None:
            if self.font_path.exists():
                with open(self.font_path, "rb") as f:
                    self._font_b64 = base64.b64encode(f.read()).decode("utf-8")
            else:
                self._font_b64 = ""
        return self._font_b64

    def _get_avatar_b64(self) -> str:
        """Returns base64 encoded page avatar image for brand embedding."""
        if self._avatar_b64 is None:
            if self.avatar_path.exists():
                with open(self.avatar_path, "rb") as f:
                    self._avatar_b64 = base64.b64encode(f.read()).decode("utf-8")
            else:
                self._avatar_b64 = ""
        return self._avatar_b64

    def render_photo_card(
        self,
        base_image_path: Path,
        headline: str,
        category: str = "",
        highlight_words: str = "",
        slot: str = "morning",
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Composes a high-impact editorial Photo Card from the base image and headline text.
        Returns the output image path.
        """
        target_path = output_path or base_image_path.with_name(f"{base_image_path.stem}_card.jpg")

        # If no browser is installed, gracefully keep the base image
        if not self.browser_bin:
            logger.info("Skipping photocard text overlay: browser not installed.")
            return base_image_path

        if not base_image_path.exists():
            logger.warning(f"Base image not found at {base_image_path}")
            return base_image_path

        try:
            # Clean headline (strip outer emojis/quotes if needed for the graphic card)
            clean_headline = self._clean_card_text(headline)
            formatted_headline = self._apply_highlights(clean_headline, highlight_words)

            theme = SLOT_THEMES.get(slot, SLOT_THEMES["morning"])
            display_category = category.strip() if category.strip() else theme["default_category"]

            # Encode background image
            with open(base_image_path, "rb") as img_file:
                bg_b64 = base64.b64encode(img_file.read()).decode("utf-8")

            font_b64 = self._get_font_b64()
            avatar_b64 = self._get_avatar_b64()
            font_face_css = ""
            if font_b64:
                font_face_css = f"""
                @font-face {{
                    font-family: 'Hind Siliguri';
                    src: url('data:font/truetype;charset=utf-8;base64,{font_b64}') format('truetype');
                    font-weight: 700;
                    font-style: normal;
                }}
                """

            avatar_html = (
                f'<img src="data:image/png;base64,{avatar_b64}" class="avatar-circle">'
                if avatar_b64
                else f'<span class="logo-icon">{theme["icon"]}</span>'
            )

            html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  {font_face_css}
  @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@600;700;800&family=Plus+Jakarta+Sans:wght@700;800&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1080px;
    height: 1080px;
    position: relative;
    overflow: hidden;
    background: #080c16;
    font-family: 'Hind Siliguri', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }}
  .bg-image {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    object-fit: cover;
    z-index: 1;
  }}
  .gradient-overlay {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(
      180deg, 
      rgba(7, 11, 20, 0.96) 0%, 
      rgba(7, 11, 20, 0.88) 35%, 
      rgba(7, 11, 20, 0.38) 64%, 
      rgba(7, 11, 20, 0.05) 100%
    );
    z-index: 2;
  }}
  .content-container {{
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    padding: 60px 70px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    z-index: 3;
  }}
  .top-meta {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 35px;
  }}
  .brand-identity {{
    display: flex;
    align-items: center;
    gap: 16px;
    background: rgba(15, 23, 42, 0.70);
    backdrop-filter: blur(14px);
    padding: 6px 22px 6px 8px;
    border-radius: 999px;
    border: 1.5px solid {theme['brand_border']};
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  }}
  .avatar-circle {{
    width: 60px;
    height: 60px;
    border-radius: 50%;
    object-fit: cover;
    border: 2.5px solid {theme['avatar_border']};
    box-shadow: 0 0 16px {theme['avatar_glow']};
  }}
  .logo-icon {{
    font-size: 32px;
    line-height: 1;
    margin-left: 6px;
  }}
  .brand-name {{
    color: #ffffff;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 0.5px;
  }}
  .category-badge {{
    background: {theme['badge_bg']};
    border: 1.5px solid {theme['badge_border']};
    color: {theme['badge_color']};
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 20px;
    font-weight: 800;
    padding: 10px 24px;
    border-radius: 999px;
    letter-spacing: 1px;
    text-transform: uppercase;
  }}
  .headline {{
    color: #ffffff;
    font-size: 52px;
    font-weight: 700;
    line-height: 1.35;
    text-shadow: 0 4px 18px rgba(0,0,0,0.85);
    max-width: 940px;
  }}
  .headline .highlight {{
    color: #facc15;
    text-shadow: 0 0 28px rgba(250, 204, 21, 0.45);
    display: inline;
  }}
</style>
</head>
<body>
  <img src="data:image/jpeg;base64,{bg_b64}" class="bg-image">
  <div class="gradient-overlay"></div>
  <div class="content-container">
    <div class="top-meta">
      <div class="brand-identity">
        {avatar_html}
        <span class="brand-name">Be Smart With AI</span>
      </div>
      <div class="category-badge">{display_category}</div>
    </div>
    <div class="headline">
      {formatted_headline}
    </div>
  </div>
</body>
</html>"""

            temp_html = TEMP_DIR / "photocard_render.html"
            with open(temp_html, "w", encoding="utf-8") as f:
                f.write(html_content)

            file_url = temp_html.resolve().as_uri()
            cmd = [
                self.browser_bin,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                f"--screenshot={str(target_path.resolve())}",
                "--window-size=1080,1080",
                "--hide-scrollbars",
                file_url
            ]

            logger.info("Executing headless browser to render editorial PhotoCard...")
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if res.returncode == 0 and target_path.exists() and target_path.stat().st_size > 5000:
                logger.info(f"🎉 PhotoCard successfully rendered at {target_path} ({target_path.stat().st_size:,} bytes)")
                return target_path
            else:
                logger.warning(f"Browser rendering returned non-zero code ({res.returncode}): {res.stderr}")
                return base_image_path

        except Exception as e:
            logger.error(f"Error rendering PhotoCard: {e}. Falling back to base image.")
            return base_image_path

    def _clean_card_text(self, text: str) -> str:
        """Removes outer quotation marks and leading emojis for a clean editorial headline."""
        cleaned = text.strip()
        # Remove common outer decorative emojis
        cleaned = re.sub(r"^[\U00010000-\U0010ffff\u2600-\u27bf\s]+", "", cleaned)
        cleaned = re.sub(r"[\U00010000-\U0010ffff\u2600-\u27bf\s]+$", "", cleaned)
        return cleaned.strip()

    def _apply_highlights(self, headline: str, highlight_words: str) -> str:
        """Applies yellow highlight formatting to key words in the headline."""
        if highlight_words and highlight_words.strip():
            clean_hw = highlight_words.strip().strip("'\"")
            # If highlight_words exists inside headline, wrap it
            if clean_hw in headline:
                return headline.replace(clean_hw, f'<span class="highlight">{clean_hw}</span>', 1)

        # Look for single-quoted or double-quoted phrases in headline
        quote_match = re.search(r"['\"](.*?)['\"]", headline)
        if quote_match:
            quoted_text = quote_match.group(0)
            inner_text = quote_match.group(1)
            return headline.replace(quoted_text, f'<span class="highlight">{inner_text}</span>', 1)

        # Fallback: highlight the last 3-4 words if no specific match
        words = headline.split()
        if len(words) >= 5:
            prefix = " ".join(words[:-3])
            highlight_part = " ".join(words[-3:])
            return f'{prefix} <span class="highlight">{highlight_part}</span>'

        return headline
