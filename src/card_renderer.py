import logging
import re
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageOps
from src.config import BASE_DIR, TEMP_DIR, AGENCY_NAME

logger = logging.getLogger(__name__)

class LinkedInCardRenderer:
    """
    Renders high-impact, modern executive B2B Infographic Cards (1080x1080 square)
    for LinkedIn posts. 100% offline, zero-browser dependency, guaranteed reliability.
    """
    def __init__(self, font_bengali_path: Optional[Path] = None, logo_path: Optional[Path] = None):
        self.font_bengali_path = font_bengali_path or (BASE_DIR / "assets" / "fonts" / "HindSiliguri-Bold.ttf")
        self.font_english_path = BASE_DIR / "assets" / "fonts" / "PlusJakartaSans-Bold.ttf"
        self.logo_path = logo_path or (BASE_DIR / "assets" / "agency_logo.jpg")

    def render_b2b_card(
        self,
        headline: str,
        category: str = "B2B AUTOMATION",
        metric: str = "Zero Delay • 24/7 Autonomous Pipeline",
        output_path: Optional[Path] = None
    ) -> Path:
        """Renders an executive dark-mode infographic card with crisp typography."""
        target_path = output_path or (TEMP_DIR / "latest_linkedin_card.jpg")
        TEMP_DIR.mkdir(exist_ok=True)

        width, height = 1080, 1080
        # Deep Obsidian Navy
        img = Image.new("RGB", (width, height), color=(11, 17, 32))
        draw = ImageDraw.Draw(img)

        # 1. Subtle Ambient Background Glow (Electric Cyan & Royal Emerald)
        for r in range(480, 0, -20):
            alpha_ratio = (r / 480)
            color_top = (int(14 * (1 - alpha_ratio) + 11), int(165 * (1 - alpha_ratio) + 17), int(233 * (1 - alpha_ratio) + 32))
            draw.ellipse([(width - r, -r), (width + r, r)], outline=color_top, width=2)

        for r in range(350, 0, -25):
            alpha_ratio = (r / 350)
            color_bot = (int(16 * (1 - alpha_ratio) + 11), int(185 * (1 - alpha_ratio) + 17), int(129 * (1 - alpha_ratio) + 32))
            draw.ellipse([(-r, height - r), (r, height + r)], outline=color_bot, width=2)

        # 2. Sleek Glassmorphism Border & Accent Lines
        margin = 45
        draw.rectangle([(margin, margin), (width - margin, height - margin)], outline=(30, 41, 59), width=2)
        # Top Cyan Accent bar
        draw.line([(margin, margin), (width - margin, margin)], fill=(14, 165, 233), width=6)

        # 3. Load Fonts
        title_font = ImageFont.truetype(str(self.font_bengali_path), 48) if self.font_bengali_path.exists() else None
        badge_font = ImageFont.truetype(str(self.font_english_path), 22) if self.font_english_path.exists() else None
        metric_font = ImageFont.truetype(str(self.font_english_path), 24) if self.font_english_path.exists() else None
        brand_font = ImageFont.truetype(str(self.font_english_path), 22) if self.font_english_path.exists() else None
        sub_font = ImageFont.truetype(str(self.font_bengali_path), 28) if self.font_bengali_path.exists() else None

        # 4. Top Header Meta: Brand Identity (Left)
        brand_box = [(margin + 35, margin + 35), (margin + 380, margin + 110)]
        draw.rounded_rectangle(brand_box, radius=25, fill=(15, 23, 42), outline=(14, 165, 233), width=2)

        # Logo Avatar
        if self.logo_path.exists():
            try:
                logo_img = Image.open(self.logo_path).convert("RGBA").resize((60, 60), Image.Resampling.LANCZOS)
                mask = Image.new("L", (60, 60), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse([(0, 0), (59, 59)], fill=255)
                img.paste(logo_img, (margin + 45, margin + 43), mask)
            except Exception as e:
                logger.debug(f"Logo paste error: {e}")

        draw.text((margin + 120, margin + 60), AGENCY_NAME, fill=(255, 255, 255), font=brand_font)

        # Category Badge (Top Right)
        cat_text = category.strip().upper()
        cat_w = len(cat_text) * 13 + 50
        cat_x1 = max(600, width - margin - cat_w - 30)
        draw.rounded_rectangle([(cat_x1, margin + 42), (width - margin - 30, margin + 102)], radius=20, fill=(16, 185, 129, 40), outline=(16, 185, 129), width=2)
        draw.text((cat_x1 + 25, margin + 60), cat_text, fill=(52, 211, 153), font=badge_font)

        # 5. Center Hero Badge
        draw.rounded_rectangle([(width//2 - 170, 240), (width//2 + 170, 295)], radius=18, fill=(15, 23, 42), outline=(14, 165, 233), width=2)
        draw.text((width//2, 267), "⚡ AI AUTOMATION CASE STUDY", fill=(56, 189, 248), anchor="mm", font=badge_font)

        # 6. Center Hero Headline (Formatted into max 3 lines with drop shadow)
        clean_headline = re.sub(r"^[\U00010000-\U0010ffff\u2600-\u27bf\s]+", "", headline).strip()
        words = clean_headline.split()
        lines = []
        curr_line = []
        for word in words:
            curr_line.append(word)
            if len(" ".join(curr_line)) > 26:
                lines.append(" ".join(curr_line))
                curr_line = []
        if curr_line:
            lines.append(" ".join(curr_line))
        lines = lines[:3]

        y_text = 370
        for line in lines:
            # Drop shadow
            draw.text((width//2 + 2, y_text + 2), line, fill=(0, 0, 0), anchor="mm", font=title_font)
            # Main white text
            draw.text((width//2, y_text), line, fill=(248, 250, 252), anchor="mm", font=title_font)
            y_text += 80

        # Sub-explainer note
        draw.text((width//2, y_text + 30), "আপনার ব্যবসাকে স্বয়ংক্রিয় করে সময় বাঁচান এবং সেলস বাড়ান", fill=(148, 163, 184), anchor="mm", font=sub_font)

        # 7. Metric / ROI Ribbon (Bottom Center)
        metric_box = [(margin + 60, height - 260), (width - margin - 60, height - 175)]
        draw.rounded_rectangle(metric_box, radius=24, fill=(15, 23, 42), outline=(16, 185, 129), width=2)
        draw.text((width//2, height - 218), f"🎯  {metric}  🎯", fill=(52, 211, 153), anchor="mm", font=metric_font)

        # 8. Bottom Footer (Official Contact & Authority)
        draw.text((width//2, height - margin - 45), "Be Smart With AI • Free Business Process Audit: wa.me/8801610594042", fill=(148, 163, 184), anchor="mm", font=brand_font)

        # Save JPEG
        img.save(target_path, "JPEG", quality=95)
        logger.info(f"✅ B2B LinkedIn Infographic Card successfully rendered: {target_path}")
        return target_path
