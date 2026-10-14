import argparse
import logging
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.config import (
    get_current_bst_time,
    determine_today_theme,
    B2B_THEMES,
    GEMINI_API_KEY,
    LINKEDIN_ACCESS_TOKEN,
    LINKEDIN_PERSON_URN,
    BUFFER_API_KEY,
    BUFFER_CHANNEL_ID,
    AGENCY_NAME
)
from src.history_manager import HistoryManager
from src.content_generator import LinkedInContentGenerator
from src.card_renderer import LinkedInCardRenderer
from src.linkedin_client import LinkedInClient
from src.buffer_client import BufferClient

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("LINKEDIN_POSTER")

def run_poster(theme_id: str = None, dry_run: bool = False, skip_image: bool = False, force: bool = False) -> None:
    now_bst = get_current_bst_time()
    logger.info("=" * 65)
    logger.info(f"💼 শুরু হচ্ছে LinkedIn B2B Client-Acquisition অটোমেশন বট ({AGENCY_NAME})")
    logger.info(f"⏰ বর্তমান সময় (বাংলাদেশ): {now_bst.strftime('%Y-%m-%d %I:%M:%S %p')} BST")

    # 1. Select Theme
    theme_data = None
    if theme_id:
        for t in B2B_THEMES.values():
            if t["theme_id"] == theme_id:
                theme_data = t
                break
    if not theme_data:
        theme_data = determine_today_theme()

    logger.info(f"🎯 আজকের স্ট্র্যাটেজিক থিম: {theme_data['name']}")
    logger.info(f"📌 টার্গেট অডিয়েন্স: {theme_data['target_audience']}")
    logger.info("=" * 65)

    # 2. History Check & 1-Post-Per-Day Guard
    history_mgr = HistoryManager()
    if not dry_run and not force:
        already_posted, last_time = history_mgr.is_already_posted_today()
        if already_posted:
            logger.warning(f"⚠️ আজকের দিনে ইতিমধ্যে একটি পোস্ট করা হয়েছে ({last_time})।")
            logger.info("🛡️ লিঙ্কডইন অ্যালগরিদম ক্যানিবালাইজেশন রোধে আজকের দ্বিতীয় রানটি স্কিপ করা হলো।")
            logger.info("💡 জরুরি প্রয়োজনে পুনরায় ফোর্স করতে '--force' ফ্ল্যাগ ব্যবহার করুন।")
            return

    recent_summary = history_mgr.get_recent_summary(limit=15)
    logger.info("📚 পূর্ববর্তী পোস্টের ইতিহাস লোড হয়েছে। ডুপ্লিকেট কনটেন্ট ফিল্টার সক্রিয়।")

    # 3. Content Generation (Google Gemini + sergebulaev/linkedin-skills Humanizer)
    logger.info("✍️ ওপেন-সোর্স linkedin-skills হিউম্যানাইজার রুলস দিয়ে B2B পোস্ট তৈরি হচ্ছে...")
    content_gen = LinkedInContentGenerator(api_key=GEMINI_API_KEY)
    post_data = content_gen.generate_post(theme_data=theme_data, recent_history_summary=recent_summary)

    headline = post_data.get("headline", "")
    card_title = post_data.get("card_title", headline)
    card_badge = post_data.get("card_badge", theme_data["category"])
    card_metric = post_data.get("card_metric", "Zero Delay • 24/7 Autonomous Pipeline")
    content = post_data.get("content", "")
    topic_summary = post_data.get("topic_summary", "")

    logger.info(f"✅ পোস্ট তৈরি সম্পন্ন: '{headline}'")

    # 4. Render Infographic Card
    card_path = None
    if not skip_image:
        logger.info("🎨 এক্সিকিউটিভ B2B ইনফোগ্রাফিক কার্ড রেন্ডার করা হচ্ছে...")
        card_renderer = LinkedInCardRenderer()
        card_path = card_renderer.render_b2b_card(
            headline=card_title,
            category=card_badge,
            metric=card_metric
        )
        logger.info(f"📸 চূড়ান্ত ইনফোগ্রাফিক প্রস্তুত: {card_path}")

    # 5. Display Preview
    print("\n" + "=" * 25 + " [LINKEDIN B2B POST PREVIEW] " + "=" * 25)
    print(content)
    print("=" * 79 + "\n")

    # 6. Dry Run Check
    if dry_run:
        logger.info("🧪 [DRY-RUN মোড সক্রিয়] লিঙ্কডইনে কোনো পোস্ট পাঠানো হয়নি। প্রিভিউ ও ইমেজ সফলভাবে জেনারেট হয়েছে।")
        return

    # 7. Publish to LinkedIn (via Buffer Official Partner or Direct REST API)
    if BUFFER_API_KEY and BUFFER_CHANNEL_ID:
        logger.info("🚀 Buffer Official Partner API দিয়ে সরাসরি LinkedIn পার্সোনাল প্রোফাইলে পোস্ট পাঠানো হচ্ছে...")
        buf_client = BufferClient(api_key=BUFFER_API_KEY, channel_id=BUFFER_CHANNEL_ID)
        try:
            post_id = buf_client.publish_post(text=content, mode="shareNow")
            logger.info(f"🎉 পোস্ট সফলভাবে লিঙ্কডইনে প্রকাশিত হয়েছে! Buffer Post ID: {post_id}")

            # Record to History
            history_mgr.record_post(
                theme_id=theme_data["theme_id"],
                headline=headline,
                summary=topic_summary,
                post_urn=str(post_id),
                card_path=str(card_path) if card_path else ""
            )
            logger.info("💾 হিস্ট্রি আপডেট সম্পন্ন। আগামীকাল নতুন বিষয় ও কেস স্টাডি নিয়ে পোস্ট হবে।")
        except Exception as e:
            logger.error(f"❌ বাফারের মাধ্যমে পোস্ট প্রকাশ করতে ব্যর্থ: {e}")
            sys.exit(1)
    else:
        logger.info("🚀 LinkedIn Official REST API দিয়ে প্রোফাইলে পোস্ট পাঠানো হচ্ছে...")
        li_client = LinkedInClient(access_token=LINKEDIN_ACCESS_TOKEN, person_urn=LINKEDIN_PERSON_URN)
        try:
            post_urn = li_client.publish_post(text=content, image_path=card_path)
            logger.info(f"🎉 পোস্ট সফলভাবে লিঙ্কডইনে প্রকাশিত হয়েছে! Post URN: {post_urn}")

            # Record to History
            history_mgr.record_post(
                theme_id=theme_data["theme_id"],
                headline=headline,
                summary=topic_summary,
                post_urn=str(post_urn),
                card_path=str(card_path) if card_path else ""
            )
            logger.info("💾 হিস্ট্রি আপডেট সম্পন্ন। আগামীকাল নতুন বিষয় ও কেস স্টাডি নিয়ে পোস্ট হবে।")
        except Exception as e:
            logger.error(f"❌ লিঙ্কডইনে পোস্ট প্রকাশ করতে ব্যর্থ: {e}")
            sys.exit(1)

def verify_credentials() -> None:
    """Verifies API credentials for Gemini and Buffer/LinkedIn."""
    logger.info("🔍 ক্রেডেনশিয়াল ভেরিফিকেশন শুরু হচ্ছে...")
    
    print("\n[১] Google Gemini API চেক:")
    if not GEMINI_API_KEY:
        print("  ❌ GEMINI_API_KEY পাওয়া যায়নি! (.env ফাইলে যোগ করুন)")
    else:
        print("  🔑 GEMINI_API_KEY সক্রিয়। টেস্ট কল করা হচ্ছে...")
        try:
            gen = LinkedInContentGenerator(api_key=GEMINI_API_KEY)
            theme = determine_today_theme()
            res = gen.generate_post(theme_data=theme, recent_history_summary="")
            print(f"  ✅ Gemini API সফলভাবে সংযুক্ত! শিরোনাম: {res.get('headline')}")
        except Exception as e:
            print(f"  ❌ Gemini API ত্রুটি: {e}")

    print("\n[২] LinkedIn (Buffer Partner) চেক:")
    if BUFFER_API_KEY and BUFFER_CHANNEL_ID:
        print("  🔑 BUFFER_API_KEY সক্রিয়। বাফার চ্যানেল পরীক্ষা করা হচ্ছে...")
        try:
            buf = BufferClient(api_key=BUFFER_API_KEY, channel_id=BUFFER_CHANNEL_ID)
            ch = buf.verify_connection()
            print(f"  ✅ বাফারের মাধ্যমে লিঙ্কডইন প্রোফাইল সফলভাবে সংযুক্ত: {ch.get('name')} ({ch.get('service')})")
        except Exception as e:
            print(f"  ❌ বাফার সংযোগ ত্রুটি: {e}")
    elif LINKEDIN_ACCESS_TOKEN:
        print("  🔑 LINKEDIN_ACCESS_TOKEN পাওয়া গেছে। সংযোগ পরীক্ষা করা হচ্ছে...")
        try:
            client = LinkedInClient(access_token=LINKEDIN_ACCESS_TOKEN, person_urn=LINKEDIN_PERSON_URN)
            info = client.verify_credentials()
            print(f"  ✅ লিঙ্কডইন অ্যাকাউন্ট সংযুক্ত: {info.get('name')} ({info.get('person_urn')})")
        except Exception as e:
            print(f"  ❌ লিঙ্কডইন সংযোগ ত্রুটি: {e}")
    else:
        print("  ⚠️ BUFFER_API_KEY অথবা LINKEDIN_ACCESS_TOKEN এখনো সেট করা হয়নি।")
    print("\n")

def main():
    parser = argparse.ArgumentParser(description="LinkedIn B2B Autonomous Client-Acquisition Engine")
    parser.add_argument("--dry-run", action="store_true", help="লিঙ্কডইনে পোস্ট না করে শুধু লোকাল প্রিভিউ দেখাবে")
    parser.add_argument("--verify", action="store_true", help="জেমিনি ও লিঙ্কডইন এপিআই সংযোগ পরীক্ষা করবে")
    parser.add_argument("--skip-image", action="store_true", help="ইমেজ ছাড়াই শুধুমাত্র টেক্সট পোস্ট তৈরি করবে")
    parser.add_argument("--force", action="store_true", help="আজকে পূর্বে পোস্ট করা হলেও জোরপূর্বক পোস্ট করবে")
    parser.add_argument("--theme-id", type=str, default=None, help="নির্দিষ্ট কোনো থিম আইডি জোরপূর্বক রান করতে")

    args = parser.parse_args()

    if args.verify:
        verify_credentials()
    else:
        run_poster(theme_id=args.theme_id, dry_run=args.dry_run, skip_image=args.skip_image, force=args.force)

if __name__ == "__main__":
    main()
