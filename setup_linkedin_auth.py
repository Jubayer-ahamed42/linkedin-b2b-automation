import http.server
import json
import logging
import socketserver
import urllib.parse
import webbrowser
import requests
from pathlib import Path
from dotenv import set_key

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

PORT = 8080
REDIRECT_URI = f"http://localhost:{PORT}/callback"
# Modern OpenID & Social Share scopes
SCOPES = "openid profile email w_member_social"

print("=" * 65)
print("🔑 LinkedIn 1-Click OAuth 2.0 টোকেন সেটআপ সহকারী")
print("=" * 65)

# Read Client ID & Secret
client_id = input("\n১. আপনার LinkedIn Client ID পেস্ট করুন: ").strip()
client_secret = input("২. আপনার LinkedIn Client Secret পেস্ট করুন: ").strip()

if not client_id or not client_secret:
    print("❌ Client ID বা Secret খালি রাখা যাবে না! দয়া করে developer.linkedin.com থেকে সংগ্রহ করুন।")
    exit(1)

auth_code = None

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed_url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed_url.query)
        
        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            success_html = """
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"><title>সফল!</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #0f172a; color: #f8fafc;">
                <h1 style="color: #38bdf8;">🎉 অনুমোদন সফল হয়েছে!</h1>
                <p style="font-size: 18px;">আপনার ব্রাউজার উইন্ডোটি বন্ধ করে টার্মিনালে ফিরে যেতে পারেন।</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode("utf-8"))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed or code missing.")

auth_url = (
    f"https://www.linkedin.com/oauth/v2/authorization?"
    f"response_type=code&"
    f"client_id={client_id}&"
    f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
    f"scope={urllib.parse.quote(SCOPES)}"
)

print(f"\n🌐 ৩. আপনার ব্রাউজারে LinkedIn অনুমোদন পেজ খোলা হচ্ছে...")
print(f"👉 যদি স্বয়ংক্রিয়ভাবে ব্রাউজার না খোলে, এই লিংকটি ব্রাউজারে পেস্ট করুন:\n{auth_url}\n")
webbrowser.open(auth_url)

with socketserver.TCPServer(("", PORT), OAuthHandler) as httpd:
    print(f"⏳ অনুমোদনের জন্য অপেক্ষা করা হচ্ছে (http://localhost:{PORT}/callback)...")
    while not auth_code:
        httpd.handle_request()

print("\n✅ Authorization Code পাওয়া গেছে! এক্সেস টোকেন নেওয়া হচ্ছে...")

# Exchange code for access token
token_url = "https://www.linkedin.com/oauth/v2/accessToken"
token_payload = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "client_id": client_id,
    "client_secret": client_secret,
    "redirect_uri": REDIRECT_URI
}

token_res = requests.post(token_url, data=token_payload, timeout=20)
if token_res.status_code != 200:
    print(f"❌ টোকেন আদান-প্রদান ব্যর্থ: {token_res.text}")
    exit(1)

token_data = token_res.json()
access_token = token_data.get("access_token")
expires_in = token_data.get("expires_in", 5184000)
days_valid = int(expires_in / 86400)

print(f"🎉 Access Token সফলভাবে জেনারেট হয়েছে! (মেয়াদ: {days_valid} দিন / প্রায় ২ মাস)")

# Get Person URN
print("🔍 প্রোফাইল URN আইডি সংগ্রহ করা হচ্ছে...")
headers = {"Authorization": f"Bearer {access_token}"}
userinfo_res = requests.get("https://api.linkedin.com/v2/userinfo", headers=headers, timeout=15)
person_urn = ""
user_name = "User"

if userinfo_res.status_code == 200:
    udata = userinfo_res.json()
    user_name = udata.get("name", "User")
    person_urn = f"urn:li:person:{udata.get('sub')}"
    print(f"✅ প্রোফাইল সংযুক্ত: {user_name} ({person_urn})")
else:
    # Fallback to me
    me_res = requests.get("https://api.linkedin.com/v2/me", headers=headers, timeout=15)
    if me_res.status_code == 200:
        mdata = me_res.json()
        person_urn = f"urn:li:person:{mdata.get('id')}"
        print(f"✅ প্রোফাইল সংযুক্ত: {person_urn}")

# Save into .env
set_key(str(ENV_FILE), "LINKEDIN_CLIENT_ID", client_id)
set_key(str(ENV_FILE), "LINKEDIN_CLIENT_SECRET", client_secret)
set_key(str(ENV_FILE), "LINKEDIN_ACCESS_TOKEN", access_token)
if person_urn:
    set_key(str(ENV_FILE), "LINKEDIN_PERSON_URN", person_urn)

print("\n" + "=" * 65)
print("💾 অভিনন্দন! আপনার .env ফাইলে ক্রেডেনশিয়াল সেভ করা হয়েছে:")
print(f"  • লিঙ্কডইন ইউজার: {user_name}")
print(f"  • মেম্বার URN: {person_urn}")
print(f"  • টোকেন মেয়াদ: {days_valid} দিন")
print("=" * 65)
print("🚀 এখন আপনি 'python main.py --dry-run' চালিয়ে প্রিভিউ দেখতে পারেন!")
