import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import requests
from src.config import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN

logger = logging.getLogger(__name__)

LINKEDIN_API_BASE = "https://api.linkedin.com"

class LinkedInClient:
    """
    Official LinkedIn REST API Client for publishing text and media posts
    to personal profiles and company pages.
    """
    def __init__(self, access_token: Optional[str] = None, person_urn: Optional[str] = None):
        self.access_token = (access_token or LINKEDIN_ACCESS_TOKEN).strip()
        self.person_urn = (person_urn or LINKEDIN_PERSON_URN).strip()
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

    def verify_credentials(self) -> Dict[str, Any]:
        """
        Verifies the access token and automatically resolves the Member URN
        via the official userinfo or me endpoint.
        """
        if not self.access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN পাওয়া যায়নি! দয়া করে .env ফাইলে বা GitHub Secrets-এ সেট করুন।")

        # 1. Try modern OpenID userinfo endpoint
        userinfo_url = f"{LINKEDIN_API_BASE}/v2/userinfo"
        try:
            r = requests.get(userinfo_url, headers=self.headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                sub = data.get("sub")
                name = data.get("name") or f"{data.get('given_name', '')} {data.get('family_name', '')}".strip()
                self.person_urn = f"urn:li:person:{sub}"
                logger.info(f"✅ LinkedIn OpenID Verified: {name} (URN: {self.person_urn})")
                return {"name": name, "person_urn": self.person_urn, "email": data.get("email")}
        except Exception as e:
            logger.debug(f"OpenID userinfo check error: {e}")

        # 2. Try legacy me endpoint
        me_url = f"{LINKEDIN_API_BASE}/v2/me"
        try:
            r = requests.get(me_url, headers=self.headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                person_id = data.get("id")
                first = data.get("localizedFirstName", "")
                last = data.get("localizedLastName", "")
                name = f"{first} {last}".strip()
                self.person_urn = f"urn:li:person:{person_id}"
                logger.info(f"✅ LinkedIn Legacy Verified: {name} (URN: {self.person_urn})")
                return {"name": name, "person_urn": self.person_urn}
            else:
                err = r.json() if "application/json" in r.headers.get("Content-Type", "") else r.text
                raise RuntimeError(f"LinkedIn Token ভেরিফিকেশন ব্যর্থ (Status {r.status_code}): {err}")
        except Exception as e:
            raise RuntimeError(f"LinkedIn API সংযোগে সমস্যা: {e}")

    def publish_post(self, text: str, image_path: Optional[Path] = None) -> str:
        """
        Publishes a post to LinkedIn.
        If image_path is provided and exists, uploads image and publishes with media.
        Otherwise, publishes a text-only UGC post.
        Returns the published Post URN.
        """
        if not self.access_token:
            raise ValueError("LINKEDIN_ACCESS_TOKEN মিসিং!")

        # Ensure person_urn is resolved
        if not self.person_urn:
            self.verify_credentials()

        if image_path and image_path.exists():
            try:
                logger.info("Uploading B2B Infographic Card to LinkedIn media storage...")
                asset_urn = self._upload_image(image_path)
                return self._publish_ugc_post(text=text, asset_urn=asset_urn)
            except Exception as e:
                logger.warning(f"Image upload to LinkedIn failed ({e}). Falling back to text post.")
                return self._publish_ugc_post(text=text, asset_urn=None)
        else:
            return self._publish_ugc_post(text=text, asset_urn=None)

    def _upload_image(self, image_path: Path) -> str:
        """Registers upload request, uploads binary, and returns the asset URN."""
        register_url = f"{LINKEDIN_API_BASE}/v2/assets?action=registerUpload"
        payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": self.person_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent"
                    }
                ]
            }
        }

        # Step 1: Register
        res = requests.post(register_url, headers=self.headers, json=payload, timeout=20)
        if res.status_code != 200:
            raise RuntimeError(f"Failed to register image upload: {res.text}")

        data = res.json()
        upload_mech = data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]
        upload_url = upload_mech["uploadUrl"]
        asset_urn = data["value"]["asset"]

        # Step 2: Upload bytes with PUT
        with open(image_path, "rb") as f:
            img_data = f.read()

        upload_headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "image/jpeg"
        }
        upload_res = requests.put(upload_url, headers=upload_headers, data=img_data, timeout=45)
        if upload_res.status_code not in [200, 201]:
            raise RuntimeError(f"Failed to upload image binary to LinkedIn (Status {upload_res.status_code})")

        logger.info(f"✅ Image binary successfully uploaded to LinkedIn: {asset_urn}")
        return asset_urn

    def _publish_ugc_post(self, text: str, asset_urn: Optional[str] = None) -> str:
        """Publishes the final UGC post to personal profile feed."""
        post_url = f"{LINKEDIN_API_BASE}/v2/ugcPosts"

        media_block = []
        if asset_urn:
            media_block = [
                {
                    "status": "READY",
                    "description": {
                        "text": "Be Smart With AI - Automation Strategy"
                    },
                    "media": asset_urn,
                    "title": {
                        "text": "B2B Automation Infographic"
                    }
                }
            ]

        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE" if asset_urn else "NONE",
                    "media": media_block
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        res = requests.post(post_url, headers=self.headers, json=payload, timeout=30)
        if res.status_code in [200, 201]:
            result = res.json()
            post_urn = result.get("id") or "published_success"
            logger.info(f"🎉 LinkedIn Post Published Successfully! Post URN: {post_urn}")
            return str(post_urn)

        err_data = res.json() if "application/json" in res.headers.get("Content-Type", "") else res.text
        raise RuntimeError(f"LinkedIn পোস্ট পাবলিশ করতে ব্যর্থ (Status {res.status_code}): {err_data}")
