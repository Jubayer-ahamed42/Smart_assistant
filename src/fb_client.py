import logging
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from src.config import FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN

logger = logging.getLogger(__name__)

GRAPH_API_VERSION = "v21.0"
GRAPH_BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

class FacebookClient:
    def __init__(self, page_id: str = None, access_token: str = None):
        self.page_id = (page_id or FB_PAGE_ID).strip()
        self.access_token = (access_token or FB_PAGE_ACCESS_TOKEN).strip()

    def verify_credentials(self) -> Dict[str, Any]:
        """
        Verifies if the Page ID and Page Access Token are valid.
        Returns Page details or raises RuntimeError with clear error description.
        """
        if not self.page_id or not self.access_token:
            raise ValueError("FB_PAGE_ID অথবা FB_PAGE_ACCESS_TOKEN পাওয়া যায়নি! দয়া করে .env বা GitHub Secrets সেট করুন।")

        url = f"{GRAPH_BASE_URL}/{self.page_id}"
        params = {
            "fields": "id,name,link",
            "access_token": self.access_token
        }
        try:
            res = requests.get(url, params=params, timeout=20)
            data = res.json()
            if res.status_code == 200:
                logger.info(f"Facebook Page Connected Successfully: {data.get('name')} (ID: {data.get('id')})")
                return data
            else:
                error_msg = data.get("error", {}).get("message", res.text)
                raise RuntimeError(f"ফেসবুক ভেরিফিকেশন ব্যর্থ হয়েছে: {error_msg}")
        except requests.RequestException as e:
            raise RuntimeError(f"ফেসবুক API সংযোগে ত্রুটি: {e}")

    def publish_post(self, message: str, image_path: Optional[Path] = None) -> str:
        """
        Publishes a post to the Facebook Page.
        If an image_path is provided and exists, publishes a Photo with caption.
        Otherwise, publishes a standard Feed post (text-only).
        Returns the published Post ID.
        """
        if not self.page_id or not self.access_token:
            raise ValueError("FB_PAGE_ID অথবা FB_PAGE_ACCESS_TOKEN সেট করা নেই!")

        # If image is available, post photo
        if image_path and image_path.exists():
            return self._publish_photo_post(message, image_path)
        else:
            return self._publish_text_post(message)

    def _publish_photo_post(self, caption: str, image_path: Path) -> str:
        """Publishes photo with caption to the page."""
        url = f"{GRAPH_BASE_URL}/{self.page_id}/photos"
        logger.info(f"Publishing photo post to Facebook Page ({self.page_id})...")

        try:
            with open(image_path, "rb") as img_file:
                files = {
                    "source": img_file
                }
                data = {
                    "caption": caption,
                    "access_token": self.access_token
                }
                res = requests.post(url, files=files, data=data, timeout=60)
                result = res.json()

                if res.status_code == 200:
                    post_id = result.get("post_id") or result.get("id")
                    logger.info(f"Photo post successfully published! Post ID: {post_id}")
                    return post_id
                else:
                    error_msg = result.get("error", {}).get("message", res.text)
                    logger.warning(f"Photo post failed ({error_msg}). Falling back to text post...")
                    return self._publish_text_post(caption)
        except Exception as e:
            logger.warning(f"Exception during photo upload: {e}. Falling back to text post...")
            return self._publish_text_post(caption)

    def _publish_text_post(self, message: str) -> str:
        """Publishes text-only post to the page feed."""
        url = f"{GRAPH_BASE_URL}/{self.page_id}/feed"
        logger.info(f"Publishing text feed post to Facebook Page ({self.page_id})...")

        payload = {
            "message": message,
            "access_token": self.access_token
        }
        res = requests.post(url, data=payload, timeout=30)
        result = res.json()

        if res.status_code == 200:
            post_id = result.get("id")
            logger.info(f"Text post successfully published! Post ID: {post_id}")
            return post_id
        else:
            error_data = result.get("error", {})
            error_msg = error_data.get("message", res.text)
            error_code = error_data.get("code")
            raise RuntimeError(f"ফেসবুকে পোস্ট পাবলিশ করতে ব্যর্থ (Code {error_code}): {error_msg}")
