"""
Unit / Functional Verification Script
Runs end-to-end local checks without requiring live Facebook credentials.
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
from src.config import determine_current_slot, SLOTS, get_current_bst_time
from src.history_manager import HistoryManager
from src.image_generator import ImageGenerator

def test_config_and_time():
    print("[Test 1] Testing Timezone and Slot Logic...")
    now_bst = get_current_bst_time()
    slot = determine_current_slot()
    print(f"  Current BST Time: {now_bst.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  Detected Slot: {slot} -> {SLOTS[slot]['theme']}")
    assert slot in ["morning", "noon", "night"]
    print("  [OK] Time & Slot logic passed!\n")

def test_history_manager():
    print("[Test 2] Testing History Manager...")
    test_history_path = Path("temp/test_history.json")
    hm = HistoryManager(history_file=test_history_path)
    
    # Clean previous test file if any
    if test_history_path.exists():
        test_history_path.unlink()

    # Record fake post
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
    print(f"  Generated Summary Preview:\n  {summary_text}")
    print("  [OK] History Manager passed!\n")

def test_image_generation():
    print("[Test 3] Testing AI Image Generation & Fallback...")
    ig = ImageGenerator()
    test_prompt = "Futuristic glowing AI brain network, holographic interface, cyan and purple cinematic light, photorealistic, 8k, no text"
    
    # Test generation (with fallback safety)
    saved_path = ig.generate_image(prompt=test_prompt, title="AI Revolution")
    assert saved_path is not None, "Image generation returned None!"
    assert saved_path.exists(), f"Image file not found at {saved_path}"
    file_size = saved_path.stat().st_size
    print(f"  [OK] Image generated successfully at {saved_path} (Size: {file_size:,} bytes)\n")

def main():
    print("=" * 60)
    print("AUTOMATED BOT COMPONENT VERIFICATION")
    print("=" * 60)
    try:
        test_config_and_time()
        test_history_manager()
        test_image_generation()
        print("ALL CORE SYSTEM TESTS PASSED SUCCESSFULLY!")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
