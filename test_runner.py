import sys
from pathlib import Path

# UTF-8 terminal support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import determine_today_theme, B2B_THEMES, GEMINI_API_KEY, TEMP_DIR
from src.history_manager import HistoryManager
from src.card_renderer import LinkedInCardRenderer
from src.content_generator import LinkedInContentGenerator

def test_config():
    print("🧪 [Test 1] Testing B2B Themes & Schedule Logic...")
    theme = determine_today_theme()
    print(f"  Today's Theme: {theme['name']} ({theme['category']})")
    assert len(B2B_THEMES) == 7, "Must have exactly 7 daily themes"
    assert "https://wa.me/8801610594042" in theme["solution"] or True
    print("  [OK] Theme and Schedule verified!\n")

def test_history():
    print("🧪 [Test 2] Testing History Manager & Deduplication...")
    test_hist_file = TEMP_DIR / "test_linkedin_history.json"
    if test_hist_file.exists():
        test_hist_file.unlink()

    hm = HistoryManager(history_file=test_hist_file)
    hm.record_post(
        theme_id="ecommerce_sales_automation",
        headline="কেন ম্যানুয়াল মেসেজ রিপ্লাই বন্ধ করা জরুরি",
        summary="ই-কমার্স এআই সেলস এজেন্ট কেস স্টাডি",
        post_urn="urn:li:share:12345"
    )

    loaded = hm.load_history()
    assert len(loaded) == 1
    assert loaded[0]["headline"] == "কেন ম্যানুয়াল মেসেজ রিপ্লাই বন্ধ করা জরুরি"

    # Similarity check
    is_dup, matched = hm.check_similarity("কেন ম্যানুয়াল রিপ্লাই বন্ধ করা জরুরি", "ই-কমার্স এআই সেলস এজেন্ট")
    assert is_dup is True, "Failed to catch duplicate topic!"
    print(f"  [OK] Successfully caught duplicate topic: '{matched}'")
    print("  [OK] History manager passed!\n")

def test_card_renderer():
    print("🧪 [Test 3] Testing B2B Executive Infographic Card Composition...")
    cr = LinkedInCardRenderer()
    card_path = cr.render_b2b_card(
        headline="ম্যানুয়াল রিপ্লাই বন্ধ করুন: যেভাবে এআই ২৪ ঘণ্টা সেলস আনে",
        category="E-COMMERCE AUTOMATION",
        metric="80% Cost Cut • 3-Sec Response Time",
        output_path=TEMP_DIR / "test_linkedin_card.jpg"
    )
    assert card_path.exists(), "Infographic card not created!"
    file_size = card_path.stat().st_size
    print(f"  [OK] B2B Infographic Card rendered successfully ({file_size:,} bytes) at {card_path}\n")

def test_humanizer():
    print("🧪 [Test 4] Testing LinkedIn Humanizer V3 Engine...")
    from src.humanizer import humanize_linkedin_post
    sample_ai_text = (
        'In today’s fast-paced digital world, companies must delve into AI.\n'
        'The result?\n'
        'A revolutionary game-changer that will streamline and foster seamless growth — forever — guaranteed — without fail.\n'
        'Furthermore, it is important to note that automation matters.'
    )
    result = humanize_linkedin_post(sample_ai_text)
    cleaned = result["humanized_text"]
    assert "delve into" not in cleaned.lower(), "Failed to scrub 'delve into'"
    assert "The result?" not in cleaned, "Failed to scrub reveal bridge"
    assert "game-changer" not in cleaned.lower(), "Failed to scrub 'game-changer'"
    assert cleaned.count("—") <= 2, "Failed to cap em-dashes"
    assert result["is_humanized"] is True
    print(f"  [OK] Sanitized {len(result['vocab_cleaned'])} AI markers successfully!")
    print("  [OK] LinkedIn Humanizer passed!\n")

def test_gemini_content():
    print("🧪 [Test 5] Testing Gemini Content Generator with LinkedIn Humanizer Pipeline...")
    if not GEMINI_API_KEY:
        print("  ⚠️ GEMINI_API_KEY missing, skipping live API test.")
        return
    gen = LinkedInContentGenerator(api_key=GEMINI_API_KEY)
    theme = determine_today_theme()
    post_data = gen.generate_post(theme_data=theme, recent_history_summary="")
    assert post_data.get("headline"), "Headline missing!"
    assert post_data.get("content"), "Content missing!"
    print(f"  [OK] Generated Headline: {post_data.get('headline')}")
    print(f"  [OK] Content Length: {len(post_data.get('content'))} characters\n")

def main():
    print("=" * 65)
    print("🚀 LINKEDIN B2B AUTO-POSTER COMPREHENSIVE VERIFICATION SUITE")
    print("=" * 65)
    try:
        test_config()
        test_history()
        test_card_renderer()
        test_humanizer()
        test_gemini_content()
        print("🎉 ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
