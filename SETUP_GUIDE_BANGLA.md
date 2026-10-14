# 📘 LinkedIn B2B অটো-পোস্টার সেটআপ গাইড (Step-by-Step Bangla Guide)

এই সিস্টেমটি আপনার লিঙ্কডইন অ্যাকাউন্টের জন্য সম্পূর্ণ স্বয়ংক্রিয়ভাবে প্রতিদিন সকাল ০৯:৪৫ BST সময়ে আকর্ষণীয় B2B অটোমেশন কেস স্টাডি, প্রবলেম-সলভিং পোস্ট এবং ডিরেক্ট হোয়াটসঅ্যাপ ফানেল পাবলিশ করার জন্য তৈরি করা হয়েছে।

---

## 🧭 আপনার যা যা লাগবে (মাত্র ২টি তথ্য):
1. **LinkedIn Client ID**
2. **LinkedIn Client Secret**
*(গুগল জেমিনি এপিআই কি অলরেডি আপনার `.env` ফাইলে সেট করা আছে)*

---

## ধাপ ১: LinkedIn Developer Portal-এ অ্যাপ তৈরি (মাত্র ২ মিনিট)

১. আপনার ব্রাউজারে যান: [https://developer.linkedin.com/](https://developer.linkedin.com/)  
২. আপনার লিঙ্কডইন আইডি দিয়ে লগইন করে উপরে ডানপাশে **"My Apps"** -> **"Create App"** বাটনে ক্লিক করুন।  
৩. সাধারণ কিছু তথ্য দিন:
   - **App name:** `Be Smart With AI Automation`
   - **LinkedIn Page:** আপনার পার্সোনাল প্রোফাইল বা পেজের নাম
   - **App logo:** আমাদের ফোল্ডারের `assets/agency_logo.jpg` ফাইলটি আপলোড করে দিন।
   - শর্তাবলীর চেকবক্সে টিক দিয়ে **"Create app"** ক্লিক করুন।

---

## ধাপ ২: অ্যাপে প্রয়োজনীয় প্রোডাক্ট ও রিডাইরেক্ট ইউআরএল যোগ করা

১. অ্যাপের ভেতর **"Products"** ট্যাবে যান।
২. **"Share on LinkedIn"** এবং **"Sign In with LinkedIn using OpenID Connect"** প্রোডাক্ট দুটির পাশে থাকা **"Request access"** বাটনে ক্লিক করুন (এটি সাথে সাথেই ফ্রি ও ইনস্ট্যান্ট চালু হয়ে যায়)।
৩. এবার **"Auth"** ট্যাবে যান:
   - **OAuth 2.0 settings** সেকশনের পাশে এডিট পেন্সিল আইকনে ক্লিক করুন।
   - **Authorized redirect URLs for your app**-এ গিয়ে **"Add redirect URL"** ক্লিক করুন।
   - এই লিংকটি বসিয়ে দিন: `http://localhost:8080/callback` (এবং সেভ দিন)।
৪. একই **"Auth"** ট্যাবের উপরে থাকা:
   - **Client ID** কপি করুন।
   - **Client Secret** কপি করুন।

---

## ধাপ ৩: ১-ক্লিকে টোকেন সংগ্রহ করা (স্বয়ংক্রিয় অ্যাসিস্ট্যান্ট)

টার্মিনালে এই কমান্ডটি রান করুন:
```bash
python setup_linkedin_auth.py
```
১. স্ক্রিপ্টটি আপনার Client ID এবং Client Secret চাইবে, পেস্ট করে দিন।  
২. সাথে সাথে আপনার ব্রাউজারে লিঙ্কডইনের অনুমোদন পেজ খুলে যাবে।  
৩. শুধু **"Allow / Agree"** ক্লিক করুন।  
৪. স্ক্রিপ্টটি নিজে নিজেই আপনার টোকেন ও পার্সন আইডি সংগ্রহ করে `.env` ফাইলে পারফেক্টলি সেভ করে দেবে! 🎉

---

## ধাপ ৪: লোকাল টেস্ট রান
প্রিভিউ ও নতুন পোস্টের ছবি দেখতে রান করুন:
```bash
python main.py --dry-run
```

সরাসরি লিঙ্কডইনে একটি টেস্ট পোস্ট পাঠাতে রান করুন:
```bash
python main.py --force
```

---

## ধাপ ৫: GitHub Actions ক্লাউড সেটআপ (২৪/৭ অটোমেশন)
১. GitHub-এ একটি নতুন Private রিপোজিটরি তৈরি করুন (যেমন: `linkedin-b2b-poster`)।
২. এই ফোল্ডারের কোড পুশ করুন:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of LinkedIn B2B auto poster"
   git branch -M main
   git remote add origin https://github.com/Jubayer-ahamed42/linkedin-b2b-poster.git
   git push -u origin main
   ```
৩. GitHub রিপোজিটরির **Settings** -> **Secrets and variables** -> **Actions**-এ গিয়ে ৩টি সিক্রেট যোগ করুন:
   - `GEMINI_API_KEY`
   - `BUFFER_API_KEY`
   - `BUFFER_CHANNEL_ID`

🎉 **অভিনন্দন!** প্রতিদিন সকাল ০৯:৪৫ BST-তে আপনার পিসি বন্ধ থাকলেও ক্লাউড থেকে স্বয়ংক্রিয়ভাবে ব্যবসায়ীদের টার্গেট করে লাইভ পোস্ট প্রকাশিত হতে থাকবে!
