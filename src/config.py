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
FB_APP_ID = os.getenv("FB_APP_ID", "").strip()
FB_APP_SECRET = os.getenv("FB_APP_SECRET", "").strip()
TIMEZONE_NAME = os.getenv("TIMEZONE", "Asia/Dhaka")

# Timezone object
try:
    TZ = pytz.timezone(TIMEZONE_NAME)
except Exception:
    TZ = pytz.timezone("Asia/Dhaka")

# Slot definitions with extensive curated focus areas to prevent repetition
SLOTS = {
    "morning": {
        "name": "সকাল ০৭:০০ (AI)",
        "theme": "Artificial Intelligence (কৃত্রিম বুদ্ধিমত্তা)",
        "description": "এআই নিউজ, নতুন এআই টুলস, জেনারেটিভ এআই, মেশিন লার্নিং, এআই এর বাস্তব প্রভাব ও ভবিষ্যৎ সম্ভাবনা।",
        "focus_areas": [
            "GenAI ও আধুনিক LLM এর নতুন ব্রেকথ্রু এবং প্রয়োগ",
            "দৈনন্দিন জীবনে কাজের গতি ও উৎপাদনশীলতা বাড়ানোর সেরা এআই টুলস",
            "এআই কোডিং অ্যাসিস্ট্যান্ট এবং সফটওয়্যার ডেভেলপমেন্টের ভবিষ্যৎ",
            "ডিপফেক শনাক্তকরণ, এআই এথিক্স ও সাইবার নিরাপত্তা",
            "স্বাস্থ্যসেবা ও জটিল রোগ নির্ণয়ে আর্টিফিশিয়াল ইন্টেলিজেন্সের বিপ্লব",
            "অটোমেটেড হিউম্যানয়েড রোবট ও আধুনিক ফ্যাক্টরি অটোমেশন",
            "অটোনোমাস বা চালকবিহীন গাড়ি ও স্মার্ট ট্রান্সপোর্টেশন",
            "এআই ভয়েস ক্লোনিং, মিউজিক জেনারেশন ও ক্রিয়েটিভ মিডিয়ার ভবিষ্যৎ",
            "শিক্ষা ও গবেষণায় পারসোনালাইজড এআই টিউটরিং প্ল্যাটফর্ম",
            "ফিন্যান্স, শেয়ার মার্কেট ও ব্যাংকিংয়ে এআই অ্যালগরিদম",
            "এআই চিপসেট (Nvidia, TPU, NPU) এবং হার্ডওয়্যার রেভোলিউশন",
            "মাল্টিমোডাল এআই মডেল (টেক্সট, ভিডিও, অডিও ও ইমেজ ইন্টিগ্রেশন)",
            "ব্যবসা ও মার্কেটিং অটোমেশনে ব্যবহৃত কার্যকর এআই স্ট্র্যাটেজি",
            "এআই এজেন্ট এবং স্বয়ংক্রিয় ডিসিশন মেকিং সিস্টেম",
            "এআই এর যুগে তরুণদের জন্য নতুন ক্যারিয়ার ও স্কিলস"
        ],
        "hashtags": ["#ArtificialIntelligence", "#AI", "#TechNews", "#FutureTech", "#বাংলা_টেক", "#BanglaTech"]
    },
    "noon": {
        "name": "দুপুর ১২:০০ (Technology)",
        "theme": "Technology & Innovation (প্রযুক্তি ও আধুনিক উদ্ভাবন)",
        "description": "স্মার্ট গ্যাজেট, কম্পিউটার সায়েন্স, সাইবার নিরাপত্তা, উদ্ভাবনী টেকনোলজি এবং আইটি জ্ঞান।",
        "focus_areas": [
            "নেক্সট-জেন স্মার্টফোন, প্রসেসর ও ৩ ন্যানোমিটার চিপসেট ইনোভেশন",
            "সাইবার সিকিউরিটি, ফিশিং আক্রমণ ও সোশ্যাল মিডিয়া অ্যাকাউন্ট সুরক্ষার উপায়",
            "ক্লাউড কম্পিউটিং ও গ্লোবাল হাইপারস্কেল ডেটা সেন্টারের পরিকাঠামো",
            "ইন্টারনেট অফ থিংস (IoT) ও স্মার্ট হোমের নিত্যনতুন গ্যাজেট",
            "সুপারকম্পিউটার, এক্সাস্কেল কম্পিউটিং ও ভবিষ্যৎ প্রসেসিং ক্ষমতা",
            "স্যাটেলাইট ইন্টারনেট (Starlink) এবং প্রত্যন্ত অঞ্চলে কানেক্টিভিটি",
            "ইলেকট্রিক ভেহিকেল (EV), সলিড স্টেট ব্যাটারি ও দ্রুত চার্জিং প্রযুক্তি",
            "অগমেন্টেড রিয়ালিটি (AR) ও ভার্চুয়াল রিয়ালিটি (VR) হেডসেটের চমক",
            "আধুনিক ওয়াইফাই (Wi-Fi 7), 5G এবং ভবিষ্যৎ 6G নেটওয়ার্ক",
            "স্মার্ট ওয়্যারেবল ও হেলথ ট্র্যাকিং ডিভাইসের সেন্সর প্রযুক্তি",
            "ওপেন সোর্স সফটওয়্যার ও আধুনিক প্রোগ্রামিং দুনিয়ার ট্রেন্ডস",
            "প্রযুক্তি জগতের মজার অজানা ইতিহাস ও সিলিকন ভ্যালির গল্প",
            "সাইবার ক্রাইম রোধে আধুনিক এনক্রিপশন ও বায়োমেট্রিক সিকিউরিটি",
            "স্মার্ট সিটি ও ডিজিটাল গভর্নেন্সের আধুনিক প্রযুক্তি"
        ],
        "hashtags": ["#Technology", "#TechInnovation", "#Gadgets", "#CyberSecurity", "#বাংলা_আইটি", "#TechWorld"]
    },
    "night": {
        "name": "রাত ০৮:০০ (Science)",
        "theme": "Science & Space (বিজ্ঞান, মহাকাশ ও আবিষ্কার)",
        "description": "মহাকাশ বিজ্ঞান, কোয়ান্টাম ফিজিক্স, বৈজ্ঞানিক আবিষ্কার, চিকিৎসা বিজ্ঞান এবং পৃথিবীর বিস্ময়।",
        "focus_areas": [
            "জেমস ওয়েব ও হাবল টেলিস্কোপের সাম্প্রতিক মহাজাগতিক আবিষ্কার",
            "ব্ল্যাকহোল, ইভেন্ট হরাইজন ও মহাকর্ষীয় তরঙ্গের গভীর রহস্য",
            "চন্দ্র ও মঙ্গল গ্রহ অভিযান এবং সৌরজগতের বাইরে প্রাণের সন্ধান (Exoplanets)",
            "কোয়ান্টাম পদার্থবিজ্ঞান, কোয়ান্টাম এন্ট্যাঙ্গলমেন্ট ও কোয়ান্টাম কম্পিউটিং",
            "জেনেটিক ইঞ্জিনিয়ারিং ও CRISPR জিন এডিটিং প্রযুক্তি",
            "গভীর সমুদ্রের রহস্যময় জীববৈচিত্র্য ও সমুদ্র তলদেশের অজানা জগত",
            "নবায়নযোগ্য জ্বালানি, নিউক্লিয়ার ফিউশন ও পরিচ্ছন্ন শক্তির ভবিষ্যৎ",
            "নিউরোসায়েন্স ও মানুষের মস্তিষ্কের নিউরাল নেটওয়ার্ক ও স্মৃতির রহস্য",
            "ডার্ক ম্যাটার ও ডার্ক এনার্জি: মহাবিশ্বের ৯৫% অজানা উপাদান",
            "পৃথিবীর চরমভাবাপন্ন আবহাওয়া, ওজোন স্তর ও ভূতাত্ত্বিক আলোড়ন",
            "অ্যান্টিম্যাটার এবং কণা পদার্থবিজ্ঞানের (CERN) বিস্ময়কর গবেষণা",
            "সময় পরিভ্রমণ (Time Dilation) এবং আইনস্টাইনের আপেক্ষিকতা তত্ত্ব",
            "মানবদেহের রোগ প্রতিরোধ ব্যবস্থা এবং আধুনিক অ্যান্টিবডি থেরাপি"
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
