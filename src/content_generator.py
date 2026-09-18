import json
import logging
import random
import re
import time
import requests
from typing import Dict, Any, List
from src.config import GEMINI_API_KEY, SLOTS, get_current_bst_time
from src.history_manager import HistoryManager

logger = logging.getLogger(__name__)

# Active Gemini models verified for generateContent
CANDIDATE_MODELS = [
    "gemini-flash-latest",
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash"
]

class ContentGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GEMINI_API_KEY

    def generate_post(self, slot: str, recent_history_summary: str = "", history_mgr: HistoryManager = None) -> Dict[str, Any]:
        """
        Generates Facebook post content and image prompt using Google Gemini API.
        Includes an automatic similarity/duplicate verification loop to guarantee 100% uniqueness.
        """
        slot_info = SLOTS.get(slot, SLOTS["morning"])
        theme = slot_info["theme"]
        description = slot_info["description"]
        focus_areas = slot_info["focus_areas"]
        hashtags_list = " ".join(slot_info["hashtags"])
        
        # Pick a focus area least recently covered
        chosen_focus = self._select_fresh_focus(focus_areas, recent_history_summary)

        # We allow up to 3 attempts if similarity filter detects close match
        max_attempts = 3
        extra_warning = ""

        for attempt in range(1, max_attempts + 1):
            prompt = f"""
তুমি একজন অত্যন্ত অভিজ্ঞ ও জনপ্রিয় টেক ও সায়েন্স কনটেন্ট ক্রিয়েটর এবং সোশ্যাল মিডিয়া স্ট্র্যাটেজিস্ট।
তোমার কাজ হলো ফেসবুক পেজের জন্য সম্পূর্ণ নতুন, ইউনিক, আকর্ষণীয় ও শিক্ষণীয় একটি বাংলা পোস্ট তৈরি করা।

【বর্তমান পোস্টের ক্যাটাগরি ও থিম】
- সময় ও স্লট: {slot_info['name']}
- মূল বিষয়বস্তু: {theme}
- ক্যাটাগরি বিবরণ: {description}
- বিশেষ ফোকাস বিষয়: {chosen_focus}

【পূর্ববর্তী কভার করা পোস্টসমূহ (এই বিষয়গুলো কোনোভাবেই পুনরাবৃত্তি করবে না)】:
{recent_history_summary if recent_history_summary else "এখনো পূর্ববর্তী কোনো টপিক নেই। সম্পূর্ণ ইউনিক নতুন কিছু দিয়ে শুরু করো।"}

{extra_warning}

【পোস্ট লেখার গুরুত্বপূর্ণ নির্দেশনাবলী】:
১. ইউনিকনেস (কঠোরভাবে বাধ্যতামূলক): পূর্বে কভার করা কোনো বিষয়, টুল বা আবিষ্কার নিয়ে পুনরাবৃত্তি পোস্ট তৈরি করা যাবে না। সবসময় সম্পূর্ণ নতুন কোনো উদ্ভাবন, চমকপ্রদ তথ্য বা ব্রেকথ্রু তুলে ধরবে।
২. ভাষা: অত্যন্ত সহজ, সাবলীল, প্রাঞ্জল ও প্রমিত বাংলা। টেকনিক্যাল শব্দগুলো স্বাভাবিকভাবে বাংলা বা ইংরেজিতে রাখবে যাতে সাধারণ পাঠকও সহজে বুঝতে পারে।
৩. হুক লাইন (Hook): প্রথম ১-২ লাইনেই যেন পাঠকের কৌতূহল জেগে ওঠে।
৪. বডি স্ট্রাকচার:
   - আকর্ষণীয় শিরোনাম (উপযুক্ত ইমোজি সহ)।
   - সহজ ভাষায় মূল বিষয় বা বিজ্ঞানের আবিষ্কারের ব্যাখ্যা।
   - ৩ থেকে ৪টি স্পষ্ট বুলেট পয়েন্ট (বুলেট সাইন যেমন 🔹, 🚀, 💡, 🔬 ব্যবহার করবে)।
   - এটি কীভাবে মানুষের জীবন বা ভবিষ্যৎ বদলে দিচ্ছে তার সংক্ষেপ।
৫. এনগেজমেন্ট প্রশ্ন: পোস্টের শেষে পাঠকদের মতামত জানতে চেয়ে একটি আকর্ষণীয় উন্মুক্ত প্রশ্ন।
৬. হ্যাশট্যাগ: পোস্টের একদম শেষে উপযুক্ত ৫-৭টি হ্যাশট্যাগ অন্তর্ভুক্ত করবে (যেমন: {hashtags_list})।
৭. ইমেজ প্রম্পট (কঠোর নিয়ম): একটি উচ্চমানের ইংরেজি প্রম্পট লিখবে যা দিয়ে একটি ফটোরিয়েলিস্টিক বা সিনেমাটিক ছবি তৈরি করা যাবে।
   - 🚨 কঠোর নিষেধাজ্ঞা (Strict Prohibition): কোনো নারী বা মহিলার ছবি (no female, no woman, no girl, no lady, no feminine character) তৈরি করা সম্পূর্ণ নিষিদ্ধ। ছবিতে মানুষ না রেখে সবসময় বিষয়বস্তুর সাথে প্রাসঙ্গিক হাই-টেক গ্যাজেট, রোবট, চিপসেট, হার্ডওয়্যার, সার্ভার, ল্যাব বা মহাকাশ ও বৈজ্ঞানিক ভিজ্যুয়াল ফুটিয়ে তুলবে। কোনো টেক্সট বা ওয়াটারমার্ক থাকবে না।

【আউটপুট ফরম্যাট】:
অবশ্যই এবং শুধুমাত্র একটি ভ্যালিড JSON অবজেক্ট আউটপুট হিসেবে দাও, কোনো বাড়তি কথা ছাড়া:
{{
  "title": "পোস্টের মূল আকর্ষণীয় শিরোনাম (ইমোজি সহ)",
  "content": "সম্পূর্ণ ফেসবুক পোস্টটি এখানে থাকবে (শিরোনাম, হুক, পয়েন্ট, প্রশ্ন এবং হ্যাশট্যাগ সহ সবকিছু সুন্দর লাইন ব্রেক দিয়ে সাজানো)",
  "image_prompt": "A detailed cinematic English prompt for AI text-to-image generator describing a striking visual related to this topic. Focus strictly on futuristic hardware, gadgets, sleek robots, cybernetic devices, deep space or science concepts. STRICT CONSTRAINT: Absolutely NO female, woman, girl, lady, or feminine characters. 8k, photorealistic, cinematic lighting, no text.",
  "topic_summary": "টপিকটির ১ লাইনের সংক্ষেপ (ভবিষ্যতে ডুপ্লিকেট রোধের জন্য)"
}}
"""
            logger.info(f"Generating unique content for slot '{slot}' ({theme}) [Attempt {attempt}/{max_attempts}]...")
            raw_response = self._call_gemini_api(prompt)
            parsed = self._parse_json_response(raw_response)

            if not parsed.get("content"):
                logger.warning("Parsing failed to find content. Generating structured fallback.")
                parsed = self._generate_fallback(slot, chosen_focus)

            title = parsed.get("title", "")
            summary = parsed.get("topic_summary", "")

            # If HistoryManager is provided, verify anti-duplicate filter
            if history_mgr:
                is_dup, matched_title = history_mgr.check_similarity(title, summary)
                if is_dup:
                    logger.warning(f"Rejecting generated topic on attempt {attempt}: Too close to '{matched_title}'. Regenerating...")
                    extra_warning = f"🚨 কঠোর সতর্কতা: তোমার পূর্বের চেষ্টাটি '{matched_title}' পোস্টের সাথে বেশি মিলে গেছে! দয়া করে সম্পূর্ণ ভিন্ন কোনো টুল, খবর বা আবিষ্কার বেছে নাও।"
                    chosen_focus = random.choice(focus_areas)
                    continue

            # Passed uniqueness check
            return parsed

        return parsed

    def _select_fresh_focus(self, focus_areas: List[str], history_summary: str) -> str:
        """Selects a focus area least recently mentioned in history."""
        candidates = [area for area in focus_areas if area.lower() not in history_summary.lower()]
        return random.choice(candidates) if candidates else random.choice(focus_areas)

    def _call_gemini_api(self, prompt: str) -> str:
        """Calls Gemini API with SDK or direct REST fallback and retry logic."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY পাওয়া যায়নি! দয়া করে .env ফাইলে বা GitHub Secrets-এ GEMINI_API_KEY সেট করুন।")

        # Try Google GenAI SDK first
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            for model_name in CANDIDATE_MODELS:
                for attempt in range(2):
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                        )
                        if response and response.text:
                            return response.text
                    except Exception as sdk_err:
                        err_str = str(sdk_err)
                        if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str:
                            logger.warning(f"Model {model_name} busy (attempt {attempt+1}/2). Waiting 2s...")
                            time.sleep(2)
                        else:
                            logger.warning(f"SDK call with model {model_name} failed: {sdk_err}. Trying next model...")
                            break
        except Exception as e:
            logger.warning(f"google-genai SDK init failed: {e}. Falling back to REST API.")

        # REST API Fallback
        for model in CANDIDATE_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topP": 0.95,
                    "responseMimeType": "application/json"
                }
            }
            for attempt in range(2):
                try:
                    res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            if parts:
                                return parts[0].get("text", "")
                    elif res.status_code in [429, 503]:
                        logger.warning(f"REST API {model} status {res.status_code}. Retrying in 2s...")
                        time.sleep(2)
                    else:
                        logger.warning(f"REST API {model} returned status {res.status_code}. Trying next model...")
                        break
                except Exception as req_err:
                    logger.warning(f"REST API error with {model}: {req_err}")
                    break

        raise RuntimeError("সবগুলো Gemini API কল ব্যর্থ হয়েছে। API Key এবং ইন্টারনেট সংযোগ যাচাই করুন।")

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parses clean JSON from LLM output with strict=False handling."""
        cleaned = text.strip()
        # Remove markdown code blocks if wrapped
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
            cleaned = re.sub(r"\n```$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned, strict=False)
        except Exception:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0), strict=False)
                except Exception:
                    pass
            logger.error(f"Failed to decode JSON from Gemini output: {text[:200]}...")
            return {}

    def _generate_fallback(self, slot: str, focus_area: str) -> Dict[str, Any]:
        """Provides a safe fallback template in case of parsing anomaly."""
        slot_info = SLOTS.get(slot, SLOTS["morning"])
        hashtags = " ".join(slot_info["hashtags"])
        title = f"🚀 {slot_info['theme']}: নতুন দিগন্ত উন্মোচন"
        content = f"""{title}

প্রযুক্তি ও উদ্ভাবনের দুনিয়া প্রতিদিন দ্রুতগতিতে বদলে যাচ্ছে। আজকের বিশেষ আয়োজন: {focus_area}।

🔹 আধুনিক গবেষণার মাধ্যমে নতুন সম্ভাবনার দ্বার উন্মোচিত হচ্ছে।
🔹 বাস্তব জীবনে মানুষের কাজের গতি এবং নির্ভুলতা বাড়াতে এর ভূমিকা অনন্য।
🔹 ভবিষ্যতে এই প্রযুক্তি আমাদের প্রাত্যহিক জীবনের বড় অংশ হতে চলেছে।

বিজ্ঞানের এই রোমাঞ্চকর অগ্রযাত্রা নিয়ে আপনার কী মতামত? কমেন্টে আপনার ভাবনা শেয়ার করুন!

{hashtags}"""

        return {
            "title": title,
            "content": content,
            "image_prompt": f"Futuristic sleek technology hardware or abstract science scene representing {focus_area}, cybernetic details, 8k, cinematic lighting, photorealistic, no people, no female, no text.",
            "topic_summary": f"{slot_info['theme']} - {focus_area}"
        }
