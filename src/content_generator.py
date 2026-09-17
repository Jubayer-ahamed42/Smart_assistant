import json
import logging
import random
import re
import requests
from typing import Dict, Any
from src.config import GEMINI_API_KEY, SLOTS, get_current_bst_time

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GEMINI_API_KEY

    def generate_post(self, slot: str, recent_history_summary: str = "") -> Dict[str, Any]:
        """
        Generates Facebook post content and image prompt using Google Gemini API.
        Returns a dict with:
        {
            'title': str,
            'content': str,
            'image_prompt': str,
            'topic_summary': str
        }
        """
        slot_info = SLOTS.get(slot, SLOTS["morning"])
        theme = slot_info["theme"]
        description = slot_info["description"]
        focus_areas = slot_info["focus_areas"]
        hashtags_list = " ".join(slot_info["hashtags"])
        chosen_focus = random.choice(focus_areas)

        prompt = f"""
তুমি একজন অত্যন্ত অভিজ্ঞ ও জনপ্রিয় টেক ও সায়েন্স কনটেন্ট ক্রিয়েটর এবং সোশ্যাল মিডিয়া স্ট্র্যাটেজিস্ট।
তোমার কাজ হলো ফেসবুক পেজের জন্য অত্যন্ত আকর্ষণীয়, শিক্ষণীয় ও ভাইরাল হওয়ার উপযোগী একটি সম্পূর্ণ বাংলা পোস্ট তৈরি করা।

【বর্তমান পোস্টের ক্যাটাগরি ও থিম】
- সময় ও স্লট: {slot_info['name']}
- মূল বিষয়বস্তু: {theme}
- ক্যাটাগরি বিবরণ: {description}
- বিশেষ ফোকাস বিষয়: {chosen_focus}

【পূর্ববর্তী কভার করা টপিকসমূহ (এই টপিকগুলো কোনোভাবেই পুনরাবৃত্তি করবে না)】:
{recent_history_summary if recent_history_summary else "এখনো পূর্ববর্তী কোনো টপিক নেই। সম্পূর্ণ ইউনিক নতুন কিছু দিয়ে শুরু করো।"}

【পোস্ট লেখার গুরুত্বপূর্ণ নির্দেশনাবলী】:
১. ভাষা: অত্যন্ত সহজ, সাবলীল, প্রাঞ্জল ও প্রমিত বাংলা। কোনো গুরুগম্ভীর বা দুর্বোধ্য সাধু শব্দ ব্যবহার করবে না। টেকনিক্যাল শব্দগুলো (যেমন AI, Quantum, Chips, Cloud, Algorithm) স্বাভাবিকভাবে বাংলা বা ইংরেজিতে রাখবে যাতে পাঠক সহজে বুঝতে পারে।
২. হুক লাইন (Hook): প্রথম ১-২ লাইনেই যেন পাঠকের কৌতূহল জেগে ওঠে এবং সম্পূর্ণ পোস্ট পড়ার আগ্রহ তৈরি হয়।
৩. বডি স্ট্রাকচার:
   - আকর্ষণীয় শিরোনাম (উপযুক্ত ইমোজি সহ)।
   - সহজ ভাষায় মূল ঘটনা, প্রযুক্তি বা বিজ্ঞানের আবিষ্কারের ব্যাখ্যা।
   - ৩ থেকে ৪টি স্পষ্ট বুলেট পয়েন্ট বা তথ্য (বুলেট সাইন যেমন 🔹, 🚀, 💡, 🔬 ব্যবহার করবে)।
   - এটি কীভাবে মানুষের জীবন বা ভবিষ্যৎ বদলে দিচ্ছে তার সংক্ষেপ।
৪. এনগেজমেন্ট প্রশ্ন: পোস্টের শেষে পাঠকদের মতামত জানতে চেয়ে একটি চমৎকার উন্মুক্ত প্রশ্ন (যেমন: "আপনার কাছে এই প্রযুক্তি কেমন মনে হয়? কমেন্টে জানান!")।
৫. হ্যাশট্যাগ: পোস্টের একদম শেষে উপযুক্ত ৫-৭টি জনপ্রিয় হ্যাশট্যাগ অন্তর্ভুক্ত করবে (যেমন: {hashtags_list})।
৬. ইমেজ প্রম্পট (Image Prompt): একটি উচ্চমানের ইংরেজি প্রম্পট লিখবে যা দিয়ে একটি ফটোরিয়েলিস্টিক বা অত্যাধুনিক থ্রিডি/সিনেমাটিক ছবি তৈরি করা যাবে। 
   - লক্ষ্য রাখবে: "Photorealistic, cinematic lighting, 8k resolution, futuristic, hyper-detailed, no text, no watermark, no letters". ছবিতে কোনো লেখা (text) আঁকা যাবে না।

【আউটপুট ফরম্যাট】:
অবশ্যই এবং শুধুমাত্র একটি ভ্যালিড JSON অবজেক্ট আউটপুট হিসেবে দাও, কোনো বাড়তি কথা বা ব্যাকটিক্স ছাড়া:
{{
  "title": "পোস্টের মূল আকর্ষণীয় শিরোনাম (ইমোজি সহ)",
  "content": "সম্পূর্ণ ফেসবুক পোস্টটি এখানে থাকবে (শিরোনাম, হুক, পয়েন্ট, প্রশ্ন এবং হ্যাশট্যাগ সহ সবকিছু সুন্দর লাইন ব্রেক দিয়ে সাজানো)",
  "image_prompt": "A detailed cinematic English prompt for AI text-to-image generator describing a striking visual related to this topic, 8k, highly detailed, photorealistic, cinematic lighting, no text.",
  "topic_summary": "টপিকটির ১ লাইনের সংক্ষেপ (ভবিষ্যতে ডুপ্লিকেট রোধের জন্য)"
}}
"""
        logger.info(f"Generating content for slot '{slot}' ({theme})...")
        raw_response = self._call_gemini_api(prompt)
        parsed = self._parse_json_response(raw_response)

        # Fallback verification if parsed empty
        if not parsed.get("content"):
            logger.warning("Parsing failed to find content. Generating clean structured fallback.")
            parsed = self._generate_fallback(slot, chosen_focus)

        return parsed

    def _call_gemini_api(self, prompt: str) -> str:
        """Calls Gemini API with SDK or direct REST fallback."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY পাওয়া যায়নি! দয়া করে .env ফাইলে বা GitHub Secrets-এ GEMINI_API_KEY সেট করুন।")

        # Try Google GenAI SDK first
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            # Try gemini-2.5-flash or gemini-1.5-flash
            for model_name in ["gemini-2.5-flash", "gemini-1.5-flash"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        return response.text
                except Exception as sdk_err:
                    logger.warning(f"SDK call with model {model_name} failed: {sdk_err}. Trying next...")
        except Exception as e:
            logger.warning(f"google-genai SDK init failed: {e}. Falling back to REST API.")

        # REST API Fallback
        models = ["gemini-2.5-flash", "gemini-1.5-flash"]
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topP": 0.95,
                    "responseMimeType": "application/json"
                }
            }
            try:
                res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
                else:
                    logger.warning(f"REST API {model} returned status {res.status_code}: {res.text}")
            except Exception as req_err:
                logger.warning(f"REST API error with {model}: {req_err}")

        raise RuntimeError("সবগুলো Gemini API কল ব্যর্থ হয়েছে। API Key এবং ইন্টারনেট সংযোগ যাচাই করুন।")

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parses clean JSON from LLM output."""
        cleaned = text.strip()
        # Remove markdown code blocks if wrapped
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
            cleaned = re.sub(r"\n```$", "", cleaned)
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract JSON object via regex
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
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
            "image_prompt": f"Futuristic technology scene representing {focus_area}, hyper-detailed, 8k, cinematic lighting, photorealistic, no text.",
            "topic_summary": f"{slot_info['theme']} - {focus_area}"
        }
