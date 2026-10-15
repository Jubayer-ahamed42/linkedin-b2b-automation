import json
import logging
import random
import re
import time
from typing import Dict, Any, List
import requests
from src.config import GEMINI_API_KEY, OFFICIAL_WHATSAPP_LINK, AGENCY_NAME, get_current_bst_time
from src.humanizer import humanize_linkedin_post

logger = logging.getLogger(__name__)

# Verified reliable & lightning-fast Gemini models
CANDIDATE_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite"
]

class LinkedInContentGenerator:
    """
    Generates high-converting, human-sounding B2B LinkedIn posts targeting
    business founders, entrepreneurs, and executives.
    
    Inspired by the open-source 'sergebulaev/linkedin-skills' content framework:
    - Zero robotic clichés (Anti-AI Humanizer Filter)
    - Scroll-stopping hooks (High Dwell-Time Optimization)
    - Concrete frameworks & ROI numbers
    - Natural, low-friction conversion CTAs to WhatsApp & DM
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or GEMINI_API_KEY

    def generate_post(self, theme_data: dict, recent_history_summary: str = "") -> Dict[str, Any]:
        """Generates a structured B2B LinkedIn post with humanized tone and visual card copy."""
        theme_name = theme_data["name"]
        category = theme_data["category"]
        target = theme_data["target_audience"]
        pain = theme_data["pain_point"]
        solution = theme_data["solution"]
        case_angle = theme_data["case_study_angle"]
        hashtags = " ".join(theme_data["hashtags"])
        current_year = get_current_bst_time().year

        prompt = f"""
তুমি একজন অত্যন্ত অভিজ্ঞ B2B Growth Consultant, এআই অটোমেশন আর্কিটেক্ট এবং 'Be Smart With AI' এজেন্সির প্রতিষ্ঠাতা।
তোমার কাজ হলো LinkedIn-এর বিজনেস ওনার, সিইও ও উদ্যোক্তাদের টার্গেট করে একটি অসাধারণ, প্রফেশনাল ও হাই-কনভার্টিং বাংলা পোস্ট তৈরি করা।

【পোস্টের থিম ও কৌশলগত ব্যাকগ্রাউন্ড】:
- মূল বিষয়: {theme_name}
- ক্যাটাগরি: {category}
- টার্গেট অডিয়েন্স: {target}
- উদ্যোক্তার পেইন পয়েন্ট: {pain}
- স্বয়ংক্রিয় সমাধান: {solution}
- কেস স্টাডি দিক: {case_angle}
- অফিশিয়াল হোয়াটসঅ্যাপ লিংক: {OFFICIAL_WHATSAPP_LINK}
- বর্তমান সাল: {current_year}

【পূর্ববর্তী কভার করা বিষয়সমূহ (কোনোভাবেই হুবহু পুনরাবৃত্তি করবে না)】:
{recent_history_summary if recent_history_summary else "এখনো পূর্ববর্তী কোনো পোস্ট নেই। সম্পূর্ণ নতুন ও আকর্ষণীয় এঙ্গেল নিয়ে লিখো।"}

【🚨 LinkedIn Humanizer V3 ও স্টাইল গাইডলাইন (Open-Source sergebulaev/linkedin-skills স্ট্যান্ডার্ড)】:
১. 🚫 নিষিদ্ধ রোবোটিক শব্দ (Strictly Forbidden AI Cliches):
   - কোনোভাবেই "In today's fast-paced digital world", "Delve into", "Revolutionize", "Tapestry", "Game changer", "Furthermore", "It is important to note"-এর মতো ক্লিশে এআই কথা বলবে না।
   - সম্পূর্ণ রক্ত-মাংসের একজন বাস্তব অভিজ্ঞ টেক ফাউন্ডারের কণ্ঠে কথা বলবে, যিনি প্রতিদিন আসল ক্লায়েন্টদের সিস্টেম অটোমেট করেন।
২. 🎯 ২০২৬ প্রুভেন হুক ফরমূলা (Hook - Line 1 & 2):
   - প্রথম লাইনে কখনোই সাধারণ প্রশ্ন ("Are you struggling with X?") দিয়ে শুরু করবে না।
   - নম্বর-ফার্স্ট ওপেনার (F7) অথবা Controlled A/B কম্প্যারিজন (F17) ব্যবহার করবে (যেমন: "গত মাসে ৩টি ই-কমার্স ক্লায়েন্টের ৮২.৪% রিপ্লাই টাইম ১৫ মিনিট থেকে নেমে এসেছে ৩ সেকেন্ডে।")
৩. 🚫 রিভিল ব্রিজ ও স্ট্যাকাটো পরিহার:
   - "The result?", "The outcome?", "Plot twist:", "Here's why:" জাতীয় কৃত্রিম প্রশ্ন-উত্তর লিখবে না। সরাসরি তথ্য তুলে ধরবে।
   - "Short. Punchy. Done." এর মতো মেকানিকাল স্ট্যাকাটো প্যারাগ্রাফ লিখবে না।
৪. 📱 মোবাইল-ফ্রেন্ডলি ড্রিপ ফরম্যাটিং (Readability):
   - কোনো বিশাল বড় প্যারাগ্রাফ লিখবে না। ১ থেকে সর্বোচ্চ ২ লাইনের পর লাইন ব্রেক দেবে।
   - পয়েন্টগুলোর জন্য পরিষ্কার বুলেট (🔹 বা 🚀) ব্যবহার করবে।
৫. 💡 বাস্তব বিজনেস সাইকোলজি ও সমস্যা-সমাধান:
   - শুধু কোডিং বা টেকনিক্যাল শব্দ নিয়ে কথা বলবে না; কথা বলবে ব্যবসায়ীর লাভ, সময় বাঁচানো, কাস্টমার স্যাটিসফ্যাকশন এবং ব্যবসার স্কেলিং নিয়ে।
   - বাংলা হবে অত্যন্ত স্মার্ট, সাবলীল ও প্রমিত—যেখানে ব্যবসায়ীরা স্বাভাবিকভাবে যেসব ইংরেজি শব্দ ব্যবহার করে (যেমন: Lead, CRM, Closing, Follow-up, SOP, Conversion, ROI) সেগুলো স্বাভাবিকভাবেই থাকবে।
৬. 🤝 সরাসরি WhatsApp-ফোকাসড কল-টু-অ্যাকশন (CTA):
   - কোনো লিঙ্কডইন ইনবক্সের অপশন দেবে না; ক্লায়েন্ট যাতে সরাসরি হোয়াটসঅ্যাপে নক দিয়ে দ্রুত যোগাযোগ শুরু করে সেভাবে বিনয়ী ও প্রফেশনাল অফার দেবে:
     "আপনার বিজনেসের বর্তমান ওয়ার্কফ্লো কীভাবে এআই দিয়ে অটোমেট করে সময় ও খরচ বাঁচাবেন—তা নিয়ে একটি ফ্রি কনসালটেশন বা সিস্টেম অডিটের জন্য সরাসরি আমাকে হোয়াটসঅ্যাপে মেসেজ দিন:
     👉 {OFFICIAL_WHATSAPP_LINK}"
৭. 🏷️ উপযুক্ত ৪-৫টি প্রফেশনাল হ্যাশট্যাগ (যেমন: {hashtags})।

【আউটপুট ফরম্যাট】:
অবশ্যই এবং শুধুমাত্র একটি ভ্যালিড JSON অবজেক্ট আউটপুট হিসেবে দাও, কোনো বাড়তি কথা ছাড়া:
{{
  "headline": "পোস্টের মূল আকর্ষক শিরোনাম (ইমোজি সহ)",
  "card_title": "ইনফোগ্রাফিক ফটোকার্ডে লেখার মতো বড় ১-২ লাইনের অত্যন্ত শক্তিশালী শিরোনাম (যেমন: ম্যানুয়াল রিপ্লাই বন্ধ করুন: যেভাবে এআই ২৪ ঘণ্টা সেলস আনে)",
  "card_badge": "সংক্ষিপ্ত ব্যাজ টেক্সট (যেমন: B2B AUTOMATION CASE STUDY, 24/7 AI SALES PIPELINE)",
  "card_metric": "ফটোকার্ডের মূল পরিসংখ্যান বা সুবিধা (যেমন: 80% Cost Cut • 3-Sec Response)",
  "content": "সম্পূর্ণ লিঙ্কডইন পোস্টটি এখানে থাকবে (হুক, গল্প/বাস্তবতা, বুলেট পয়েন্ট, সমাধান, কল-টু-অ্যাকশন এবং হ্যাশট্যাগ সহ সবকিছু সুন্দর লাইন ব্রেক দিয়ে সাজানো)",
  "topic_summary": "টপিকটির ১ লাইনের সংক্ষেপ (ভবিষ্যতে ডুপ্লিকেট রোধের জন্য)"
}}
"""

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Generating B2B LinkedIn post for '{theme_name}' [Attempt {attempt}/{max_attempts}]...")
            parsed = {}
            try:
                raw_response = self._call_gemini_api(prompt)
                parsed = self._parse_json_response(raw_response)
            except Exception as e:
                logger.warning(f"Gemini API attempt {attempt} failed: {e}")
                if attempt == max_attempts:
                    parsed = self._generate_fallback(theme_data)

            if parsed and parsed.get("content"):
                # Run through LinkedIn Humanizer V3 pipeline
                humanized = humanize_linkedin_post(parsed["content"])
                parsed["content"] = humanized["humanized_text"]
                parsed["humanizer_audit"] = humanized
                logger.info(f"LinkedIn Humanizer Pass Complete: Final {humanized['word_count']} words, "
                            f"{len(humanized['vocab_cleaned'])} AI markers sanitized.")
                return parsed

        return self._generate_fallback(theme_data)

    def _call_gemini_api(self, prompt: str) -> str:
        """Calls Gemini API using SDK or direct REST fallback."""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY পাওয়া যায়নি! দয়া করে .env ফাইলে GEMINI_API_KEY সেট করুন।")

        # Try Google GenAI SDK
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
                            logger.warning(f"Model {model_name} busy. Retrying in 2s...")
                            time.sleep(2)
                        else:
                            break
        except Exception as e:
            logger.debug(f"SDK call failed, using REST fallback: {e}")

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
            try:
                res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=25)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
            except Exception as req_err:
                logger.debug(f"REST API error with {model}: {req_err}")

        raise RuntimeError("সবগুলো Gemini API কল ব্যর্থ হয়েছে।")

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Cleans and extracts JSON payload from LLM output."""
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```\s*$", "", cleaned)
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
        return {}

    def _generate_fallback(self, theme_data: dict) -> Dict[str, Any]:
        """Guaranteed high-quality B2B fallback post if API times out."""
        theme_name = theme_data["name"]
        pain = theme_data["pain_point"]
        solution = theme_data["solution"]
        hashtags = " ".join(theme_data["hashtags"])

        title = f"🚀 {theme_name}: ব্যবসার নতুন গতি"
        content = f"""{title}

অনেক ব্যবসাই প্রতিদিন একটি মারাত্মক ভুলের কারণে তাদের লাভ হারাচ্ছে:
"{pain}"

ব্যবসার স্কেলিং মানে আরও বেশি কর্মচারী নিয়োগ করে সারাদিন মেসেজ টাইপ করানো নয়। আসল স্কেলিং হলো সিস্টেম তৈরি করা।

আমরা যেভাবে এআই অটোমেশন দিয়ে সমাধান করি:
🔹 ২৪/৭ স্বয়ংক্রিয় রেসপন্স: কাস্টমার যখনই নক দিক, ৩ সেকেন্ডের ভেতর সমাধান।
🔹 জিরো হিউম্যান এরর: কাস্টমারের নাম, ফোন নম্বর ও অর্ডার ডাটা সরাসরি সিআরএম বা গুগল শিটে এন্ট্রি।
🔹 খরচ ও সময় সাশ্রয়: পুনরাবৃত্তিমূলক কাজের ৮০% সময় বেঁচে যাওয়া, যা ব্যবসার গ্রোথে কাজে লাগানো যায়।

{solution}

আপনার বিজনেসের বর্তমান ওয়ার্কফ্লো কীভাবে এআই দিয়ে অটোমেট করে সময় ও খরচ বাঁচাবেন?
একটি ফ্রি কনসালটেশন বা সিস্টেম অডিটের জন্য সরাসরি আমাকে হোয়াটসঅ্যাপে মেসেজ দিন:
👉 {OFFICIAL_WHATSAPP_LINK}

{hashtags}"""

        humanized = humanize_linkedin_post(content)
        return {
            "headline": title,
            "card_title": f"{theme_name}",
            "card_badge": theme_data.get("category", "AI AUTOMATION"),
            "card_metric": "Zero Delay • 24/7 Autonomous Pipeline",
            "content": humanized["humanized_text"],
            "humanizer_audit": humanized,
            "topic_summary": f"B2B Automation: {theme_name}"
        }
