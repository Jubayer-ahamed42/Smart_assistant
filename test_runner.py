"""
Comprehensive Unit & Functional Verification Suite
Validates all components of the autonomous bot.
"""
import sys
import io

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pathlib import Path
from src.config import (
    determine_current_slot,
    SLOTS,
    get_current_bst_time,
    GEMINI_API_KEY,
    FB_PAGE_ID,
    FB_PAGE_ACCESS_TOKEN
)
from src.history_manager import HistoryManager
from src.image_generator import ImageGenerator
from src.content_generator import ContentGenerator
from src.fb_client import FacebookClient

def test_config_and_time():
    print("🧪 [Test 1] Testing Timezone and Slot Logic...")
    now_bst = get_current_bst_time()
    slot = determine_current_slot()
    print(f"  Current BST Time: {now_bst.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  Detected Slot: {slot} -> {SLOTS[slot]['theme']}")
    assert slot in ["morning", "noon", "afternoon", "night"]
    print("  [OK] Time & Slot logic passed!\n")

def test_history_manager():
    print("🧪 [Test 2] Testing History Manager...")
    test_history_path = Path("temp/test_history.json")
    hm = HistoryManager(history_file=test_history_path)
    
    if test_history_path.exists():
        test_history_path.unlink()

    hm.record_post(
        slot="morning",
        theme="Artificial Intelligence",
        title="টেস্ট টাইটেল ১",
        summary="এআই ভিত্তিক ডেটা অ্যানালাইসিস",
        post_id="12345"
    )
    
    history = hm.load_history()
    assert len(history) == 1
    assert history[0]["title"] == "টেস্ট টাইটেল ১"

    summary_text = hm.get_recent_topics_summary(slot="morning")
    print(f"  Summary Preview: {summary_text.strip()}")

    # Test Similarity Detection (Anti-duplicate)
    is_dup, matched = hm.check_similarity("টেস্ট টাইটেল ১", "এআই ডেটা অ্যানালাইসিস")
    assert is_dup is True, "Failed to catch duplicate topic!"
    print(f"  [OK] Successfully caught duplicate topic: '{matched}'")

    is_not_dup, _ = hm.check_similarity("কোয়ান্টাম কম্পিউটিং এর ভবিষ্যৎ", "সুপার কম্পিউটারের নতুন অগ্রগতি")
    assert is_not_dup is False, "False positive duplicate detected!"
    print("  [OK] Successfully approved unique new topic!")
    print("  [OK] History Manager passed!\n")

def test_image_generation():
    print("🧪 [Test 3] Testing AI Image Generation & Fallback...")
    ig = ImageGenerator()
    test_prompt = "Futuristic glowing AI neural network, cyan and purple cinematic light, photorealistic, 8k, no text"
    
    saved_path = ig.generate_image(
        prompt=test_prompt,
        title="AI Innovation",
        hero_keywords=["Artificial intelligence neural network", "Deep learning"],
        slot="morning"
    )
    assert saved_path is not None, "Image generation returned None!"
    assert saved_path.exists(), f"Image file not found at {saved_path}"
    file_size = saved_path.stat().st_size
    print(f"  [OK] Image generated at {saved_path} ({file_size:,} bytes)\n")

def test_gemini_content_generation():
    print("🧪 [Test 4] Testing Gemini Content Generator...")
    if not GEMINI_API_KEY:
        print("  ⚠️ GEMINI_API_KEY missing, skipping live API call.")
        return
    
    cg = ContentGenerator(api_key=GEMINI_API_KEY)
    post_data = cg.generate_post(slot="morning", recent_history_summary="")
    assert post_data.get("title"), "Post title is empty!"
    assert post_data.get("content"), "Post content is empty!"
    print(f"  [OK] Gemini Generated Title: {post_data.get('title')}")
    print(f"  [OK] Content Length: {len(post_data.get('content'))} characters\n")

def test_facebook_connection():
    print("🧪 [Test 5] Testing Facebook Page Connection & Token Health...")
    if not FB_PAGE_ID or not FB_PAGE_ACCESS_TOKEN:
        print("  ⚠️ FB credentials missing, skipping Facebook check.")
        return
    
    fb = FacebookClient(page_id=FB_PAGE_ID, access_token=FB_PAGE_ACCESS_TOKEN)
    info = fb.verify_credentials()
    assert info.get("name"), "Failed to retrieve page name!"
    print(f"  [OK] Connected to Facebook Page: {info.get('name')} (ID: {info.get('id')})")
    print(f"  [OK] Token Expiration: {info.get('expires_at')} ({info.get('days_remaining')} days remaining)\n")

def main():
    print("=" * 60)
    print("🚀 AUTOMATED BOT COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 60)
    try:
        test_config_and_time()
        test_history_manager()
        test_image_generation()
        test_gemini_content_generation()
        test_facebook_connection()
        print("🎉 ALL 5 VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
