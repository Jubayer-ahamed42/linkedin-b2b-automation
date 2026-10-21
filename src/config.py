import os
from datetime import datetime
from pathlib import Path
import pytz
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "linkedin_history.json"
TEMP_DIR = BASE_DIR / "temp"

# Ensure temp directory exists
TEMP_DIR.mkdir(exist_ok=True)

# Credentials
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID", "").strip()
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET", "").strip()
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "").strip()
LINKEDIN_PERSON_URN = os.getenv("LINKEDIN_PERSON_URN", "").strip()
BUFFER_API_KEY = os.getenv("BUFFER_API_KEY", "").strip()
BUFFER_CHANNEL_ID = os.getenv("BUFFER_CHANNEL_ID", "").strip()
TIMEZONE_NAME = os.getenv("TIMEZONE", "Asia/Dhaka")

# Timezone object
try:
    TZ = pytz.timezone(TIMEZONE_NAME)
except Exception:
    TZ = pytz.timezone("Asia/Dhaka")

# Agency Details
AGENCY_NAME = "Be Smart With AI"
FOUNDER_TITLE = "Founder, Be Smart With AI | AI Automation & Systems Specialist"
OFFICIAL_WHATSAPP_LINK = "https://wa.me/8801610594042"
OFFICIAL_WHATSAPP_NUM = "+8801610594042"

# 7 Rotating Strategic B2B Automation Themes (1 post per day schedule)
B2B_THEMES = {
    0: {  # Monday
        "theme_id": "ecommerce_sales_automation",
        "name": "E-Commerce 24/7 AI Sales Closer & Order Automator",
        "category": "E-COMMERCE AUTOMATION",
        "target_audience": "E-Commerce Founders, F-Commerce Page Owners, Retail Brands",
        "pain_point": "Customers message at midnight or on holidays, wait 30 minutes, get frustrated, and buy from competitors.",
        "solution": "An intelligent 24/7 AI Sales Agent that politely answers inquiries in natural human tone, recommends relevant products, answers FAQs, and logs orders autonomously.",
        "case_study_angle": "How an online brand recovered 40% of abandoned nighttime inquiries with a zero-delay AI closer.",
        "hashtags": ["#AIAutomation", "#EcommerceGrowth"]
    },
    1: {  # Tuesday
        "theme_id": "whatsapp_crm_lead_capture",
        "name": "WhatsApp & Messenger Lead-to-CRM Instant Synchronization",
        "category": "LEAD GENERATION & CRM",
        "target_audience": "B2B Agencies, Consultants, Real Estate Brokers, Service Providers",
        "pain_point": "Hot leads get lost in endless Messenger/WhatsApp chats; follow-ups are forgotten or delayed by days.",
        "solution": "Automated workflow that captures customer details in 3 seconds, syncs them to Google Sheets/CRM, and notifies the team on Telegram/WhatsApp immediately.",
        "case_study_angle": "Never lose a high-ticket client again: The 3-second lead qualification pipeline.",
        "hashtags": ["#LeadGeneration", "#CRMAutomation"]
    },
    2: {  # Wednesday
        "theme_id": "customer_support_cost_reduction",
        "name": "Customer Support Automation: 80% Workload Cut at 1/5th Cost",
        "category": "OPERATIONAL EFFICIENCY",
        "target_audience": "Startup Founders, Operations Managers, Growing Businesses",
        "pain_point": "Support reps answering the exact same 15 questions 200 times a day; high salary costs and staff burnout.",
        "solution": "Automating 80% of repetitive Tier-1 queries instantly with a trained AI knowledge assistant, letting humans handle only high-value issues.",
        "case_study_angle": "Cutting response time from 18 minutes to 4 seconds while saving 60+ man-hours weekly.",
        "hashtags": ["#CustomerSupport", "#CostReduction"]
    },
    3: {  # Thursday
        "theme_id": "invoicing_payment_order_workflows",
        "name": "Automated Invoicing, Payment Notifications & PDF Generation",
        "category": "FINANCE & WORKFLOW AUTOMATION",
        "target_audience": "Trading Companies, Wholesale Businesses, Freelance Agencies",
        "pain_point": "Manual invoice creation in Excel, manual payment checking, and delayed receipts causing cashflow slowdowns.",
        "solution": "1-Click automated order-to-invoice engine: payment detected -> PDF generated -> sent via WhatsApp & Email in 5 seconds.",
        "case_study_angle": "How automated billing eliminates bookkeeping errors and accelerates client payments.",
        "hashtags": ["#InvoicingTech", "#ProcessAutomation"]
    },
    4: {  # Friday
        "theme_id": "booking_qualification_engine",
        "name": "Automated Meeting Booking & Client Qualification Engine",
        "category": "APPOINTMENT AUTOMATION",
        "target_audience": "Doctors, Clinics, Coaching Centers, Visa Consultancies, Law Firms",
        "pain_point": "Hours wasted back-and-forth asking 'When are you free?', dealing with no-shows, and talking to unqualified tire-kickers.",
        "solution": "Automated qualification bot that filters serious clients first, books calendar slots, takes deposit info, and sends automated reminder SMS/WhatsApp.",
        "case_study_angle": "Eliminating no-shows by 75% using multi-channel automated calendar reminders.",
        "hashtags": ["#AppointmentBooking", "#BusinessAutomation"]
    },
    5: {  # Saturday
        "theme_id": "cold_lead_reactivation",
        "name": "Dead Lead Database Reactivation via Intelligent Sequences",
        "category": "REVENUE RECOVERY",
        "target_audience": "Any business with an old phone number/email list of 500+ past inquiries",
        "pain_point": "Thousands of past leads sitting completely forgotten in spreadsheets that cost money to acquire.",
        "solution": "Automated re-engagement sequences that reach out with personalized, non-spammy offers to revive dormant prospects into fresh paying clients.",
        "case_study_angle": "Generating $2,500+ in sales from a 'dead' contact list in 48 hours without spending on new ads.",
        "hashtags": ["#LeadReactivation", "#SalesGrowth"]
    },
    6: {  # Sunday
        "theme_id": "founder_systems_over_sweat",
        "name": "Founder Freedom: Working ON Your Business, Not IN Your Business",
        "category": "EXECUTIVE LEADERSHIP",
        "target_audience": "Entrepreneurs, Small Business Owners, Solopreneurs",
        "pain_point": "Founder is trapped 14 hours a day micromanaging small repetitive tasks; cannot take a day off without business stopping.",
        "solution": "Transforming chaotic manual tasks into autonomous digital standard operating procedures (SOPs) powered by code and AI.",
        "case_study_angle": "The difference between owning a job vs owning an automated self-running business system.",
        "hashtags": ["#BusinessSystems", "#FounderLife"]
    }
}

def get_current_bst_time():
    """Returns the current datetime in Bangladesh Standard Time."""
    return datetime.now(TZ)

def determine_today_theme() -> dict:
    """Returns today's strategic theme based on day of week (0=Monday..6=Sunday)."""
    now = get_current_bst_time()
    weekday = now.weekday()
    return B2B_THEMES.get(weekday, B2B_THEMES[0])
