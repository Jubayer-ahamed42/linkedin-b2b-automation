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
        hashtags = " ".join(theme_data["hashtags"][:2])
        current_year = get_current_bst_time().year

        prompt = f"""
You are the founder and lead AI systems architect at '{AGENCY_NAME}', an elite automation consultancy helping international founders, agency owners, and growing companies replace manual operational drag with autonomous digital systems.

Your objective: Write an exceptional, high-converting, deeply human LinkedIn post in natural, conversational, executive-level English targeting B2B Founders, CEOs, and Operations Leaders.

【STRATEGIC CONTEXT & CORE THEME】:
- Theme: {theme_name}
- Category: {category}
- Target Audience: {target}
- Founder Pain Point: {pain}
- Automated Architecture / Solution: {solution}
- Real Case Study Angle: {case_angle}
- Official Direct Consultation Link: {OFFICIAL_WHATSAPP_LINK}
- Current Year: {current_year}

【PREVIOUSLY COVERED ANGLES (DO NOT REPEAT TOPICS)】:
{recent_history_summary if recent_history_summary else "No previous posts recorded. Present a fresh, compelling, numbers-backed case study."}

【🚨 STRICT 2026 LINKEDIN HUMANIZER & VOICE GUIDELINES (sergebulaev/linkedin-skills standard)】:
1. 🚫 ZERO ROBOTIC CLICHÉS & AI TELLS (Penalized by LinkedIn Algorithm & Ignored by Founders):
   - ABSOLUTELY FORBIDDEN: "In today's fast-paced digital world", "Delve into", "Revolutionize", "Tapestry", "Game changer", "Furthermore", "It is important to note that", "Let that sink in", "Unleash", "Testament to".
   - AVOID AI BUZZWORD DENSITY: Do not pack paragraphs with words like crucial, significant, robust, leverage, streamline, holistic, multifaceted, elevate, empower, seamless, ecosystem. Replace with concrete facts, tangible numbers, and direct actions.
   - Speak in the calm, confident, battle-tested voice of a real practitioner who writes webhooks, connects APIs, fixes database bottlenecks, and protects client margins every day.

2. 🎯 SCROLL-STOPPING 2026 HOOK (Lines 1 & 2):
   - Never open with a generic question ("Are you struggling with X?", "Did you know that...?").
   - Open with an Odd-Precision Operational Opener (F7), Controlled A/B Comparison (F17), or Platform/Operational Risk (F1):
     * e.g., "Last month, a single autonomous workflow handled 1,840 incoming client inquiries with an average reply time of 3.4 seconds."
     * e.g., "Agency A: 4 full-time staff spending 16 hours a week copy-pasting lead data into spreadsheets. Agency B: 1 operator + a 5-step webhook sync that runs in 2 seconds."
     * e.g., "Your sales reps aren't burning out from high deal volume. They are burning out from typing the exact same 12 FAQ answers 150 times a day."

3. 🚫 ELIMINATE REVEAL BRIDGES & ARTIFICIAL RHYTHM:
   - No formulaic transition questions ("The result?", "The outcome?", "Plot twist:", "Here's why:", "Why does this matter?"). State facts directly.
   - No forced mechanical staccato stacks ("No fluff. No stress. Just scale.").
   - No stacked triads on every point (vary sentence length naturally).

4. 📱 MOBILE-OPTIMIZED READABILITY:
   - Max 1 to 2 sentences per paragraph, separated by blank lines.
   - Clear, clean bullet points (• or 🔹) for ease of skimming.
   - Ground claims with concrete numbers: hours saved per week, response time drop, dollars recovered, margin expansion.

5. 🤝 HIGH-CONVERTING, LOW-FRICTION CALL TO ACTION (CTA):
   - No fake engagement bait ("Comment 'AI' below").
   - Offer a direct, respectful, founder-to-founder invitation:
     "If you want to identify where manual data entry and repetitive tasks are creating bottlenecks in your business, message me directly on WhatsApp for a complimentary 15-minute workflow audit:
     👉 {OFFICIAL_WHATSAPP_LINK}"

6. 🏷️ STRICT MAXIMUM 2 HASHTAGS: Include strictly maximum 1 to 2 ultra-relevant hashtags at the very bottom (e.g., {hashtags}). UNDER NO CIRCUMSTANCES include more than 2 hashtags. Never place hashtags inside body sentences.

【REQUIRED OUTPUT FORMAT】:
Output strictly a valid JSON object with NO surrounding markdown commentary:
{{
  "headline": "Scroll-stopping post headline with clean emoji",
  "card_title": "Crisp, powerful 1-2 line headline for the 1080x1080 infographic card (e.g., Stop Answering FAQs Manually: How AI Closes Deals 24/7)",
  "card_badge": "Short badge text (e.g., B2B AI AUTOMATION, 24/7 SALES PIPELINE, CRM WORKFLOW)",
  "card_metric": "Key metric or ROI ribbon (e.g., 80% Cost Reduction • 3-Sec Response Time)",
  "content": "The full LinkedIn post text with hook, real breakdown, architecture bullets, ROI numbers, CTA, and hashtags properly spaced",
  "topic_summary": "1-line executive summary of the case study for future deduplication"
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
        hashtags = " ".join(theme_data["hashtags"][:2])

        title = f"⚡ {theme_name}: Eliminating Operational Bottlenecks"
        content = f"""{title}

Most growing businesses bleed margins to an avoidable operational leak:
"{pain}"

Scaling your operations does not mean hiring more people to manually copy-paste messages all day. Real scaling means building reliable systems that work without you.

Here is the exact architecture we deploy:
• 24/7 Autonomous Response: Every inquiry is answered and routed within 3 seconds, day or night.
• Zero Human Data Entry: Customer details, contact info, and deal stages sync directly to your CRM.
• Recaptured Founder Time: Over 70% of repetitive operational volume eliminated, freeing your team for high-ticket closing.

{solution}

Want to audit your current business workflows and see where automation can save 20+ hours a week?
Send me a direct message on WhatsApp for a complimentary 15-minute systems audit:
👉 {OFFICIAL_WHATSAPP_LINK}

{hashtags}"""

        humanized = humanize_linkedin_post(content)
        return {
            "headline": title,
            "card_title": f"{theme_name}",
            "card_badge": theme_data.get("category", "B2B AI AUTOMATION"),
            "card_metric": "Zero Delay • 24/7 Autonomous Pipeline",
            "content": humanized["humanized_text"],
            "humanizer_audit": humanized,
            "topic_summary": f"B2B Automation: {theme_name}"
        }
