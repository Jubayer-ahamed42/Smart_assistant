import os
from datetime import datetime
from pathlib import Path
import pytz
from dotenv import load_dotenv

# Load local .env if available
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "post_history.json"
TEMP_DIR = BASE_DIR / "temp"

# Ensure temp directory exists
TEMP_DIR.mkdir(exist_ok=True)

# Environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
FB_PAGE_ID = os.getenv("FB_PAGE_ID", "").strip()
FB_PAGE_ACCESS_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN", "").strip()
TIMEZONE_NAME = os.getenv("TIMEZONE", "Asia/Dhaka")

# Timezone object
try:
    TZ = pytz.timezone(TIMEZONE_NAME)
except Exception:
    TZ = pytz.timezone("Asia/Dhaka")

# Slot definitions
SLOTS = {
    "morning": {
        "name": "সকাল ০৭:০০ (AI)",
        "theme": "Artificial Intelligence (কৃত্রিম বুদ্ধিমত্তা)",
        "description": "এআই নিউজ, নতুন এআই টুলস, জেনারেটিভ এআই, মেশিন লার্নিং, এআই এর বাস্তব প্রভাব ও ভবিষ্যৎ সম্ভাবনা।",
        "focus_areas": [
            "GenAI ও LLM এর নতুন প্রযুক্তি",
            "দৈনন্দিন জীবনে কাজের গতি বাড়ানোর এআই টুলস",
            "এআই বিপ্লব এবং চাকরির ভবিষ্যৎ",
            "রোবোটিক্স ও অটোমেশন প্রযুক্তি",
            "স্বাস্থ্য, শিক্ষা ও গবেষণায় এআই এর ব্যবহার"
        ],
        "hashtags": ["#ArtificialIntelligence", "#AI", "#TechNews", "#FutureTech", "#বাংলা_টেক", "#BanglaTech"]
    },
    "noon": {
        "name": "দুপুর ১২:০০ (Technology)",
        "theme": "Technology & Innovation (প্রযুক্তি ও আধুনিক উদ্ভাবন)",
        "description": "স্মার্ট গ্যাজেট, কম্পিউটার সায়েন্স, সাইবার নিরাপত্তা, উদ্ভাবনী টেকনোলজি এবং আইটি জ্ঞান।",
        "focus_areas": [
            "নতুন স্মার্ট গ্যাজেট এবং চিপসেট ইনোভেশন",
            "সাইবার সিকিউরিটি ও ব্যক্তিগত ডেটা সুরক্ষার টিপস",
            "ক্লাউড কম্পিউটিং এবং ইন্টারনেট অফ থিংস (IoT)",
            "কম্পিউটার হার্ডওয়্যার ও সুপারকম্পিউটার",
            "টেক দুনিয়ার আকর্ষণীয় অজানা তথ্য ও ইতিহাস"
        ],
        "hashtags": ["#Technology", "#TechInnovation", "#Gadgets", "#CyberSecurity", "#বাংলা_আইটি", "#TechWorld"]
    },
    "night": {
        "name": "রাত ০৮:০০ (Science)",
        "theme": "Science & Space (বিজ্ঞান, মহাকাশ ও আবিষ্কার)",
        "description": "মহাকাশ বিজ্ঞান, কোয়ান্টাম ফিজিক্স, বৈজ্ঞানিক আবিষ্কার, চিকিৎসা বিজ্ঞান এবং পৃথিবীর বিস্ময়।",
        "focus_areas": [
            "নাসার মিশন, জেমস ওয়েব টেলিস্কোপ ও মহাকাশ গবেষণা",
            "কোয়ান্টাম পদার্থবিজ্ঞান ও পরমাণুর রহস্য",
            "চিকিৎসা বিজ্ঞানের যুগান্তকারী আবিষ্কার",
            "জলবায়ু বিজ্ঞান, নবায়নযোগ্য জ্বালানি ও পরিবেশ",
            "জীববিজ্ঞান এবং মহাবিশ্বের গভীর রহস্য"
        ],
        "hashtags": ["#Science", "#SpaceScience", "#Universe", "#Discovery", "#বিজ্ঞান_চর্চা", "#BanglaScience"]
    }
}

def get_current_bst_time():
    """Returns the current datetime in Bangladesh Standard Time."""
    return datetime.now(TZ)

def determine_current_slot() -> str:
    """
    Determines the slot (morning, noon, night) based on current hour in Bangladesh.
    - 05:00 - 09:59 => morning (7 AM target)
    - 10:00 - 15:59 => noon (12 PM target)
    - 16:00 - 04:59 => night (8 PM target)
    """
    now = get_current_bst_time()
    hour = now.hour

    if 5 <= hour < 10:
        return "morning"
    elif 10 <= hour < 16:
        return "noon"
    else:
        return "night"
