"""
Official Buffer GraphQL API Client for publishing text and media posts
to LinkedIn Personal Profiles without needing custom LinkedIn apps or pages.
"""

import logging
from typing import Optional, Dict, Any
import requests
from src.config import BUFFER_API_KEY, BUFFER_CHANNEL_ID

logger = logging.getLogger(__name__)

BUFFER_GRAPHQL_ENDPOINT = "https://api.buffer.com"

class BufferClient:
    """Client for publishing posts via Buffer's official GraphQL API."""

    def __init__(self, api_key: Optional[str] = None, channel_id: Optional[str] = None):
        self.api_key = (api_key or BUFFER_API_KEY).strip()
        self.channel_id = (channel_id or BUFFER_CHANNEL_ID).strip()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def verify_connection(self) -> Dict[str, Any]:
        """Verifies connection to Buffer and retrieves the linked channel details."""
        if not self.api_key:
            raise ValueError("BUFFER_API_KEY পাওয়া যায়নি! দয়া করে .env ফাইলে BUFFER_API_KEY সেট করুন।")
        if not self.channel_id:
            raise ValueError("BUFFER_CHANNEL_ID পাওয়া যায়নি! দয়া করে .env ফাইলে BUFFER_CHANNEL_ID সেট করুন।")

        query = """
        query GetChannel($input: ChannelInput!) {
            channel(input: $input) {
                id
                name
                service
            }
        }
        """
        payload = {
            "query": query,
            "variables": {"input": {"id": self.channel_id}}
        }

        res = requests.post(BUFFER_GRAPHQL_ENDPOINT, headers=self.headers, json=payload, timeout=20)
        if res.status_code != 200:
            raise RuntimeError(f"Buffer API Error (Status {res.status_code}): {res.text}")

        data = res.json()
        if "errors" in data:
            raise RuntimeError(f"Buffer GraphQL Error: {data['errors']}")

        channel_info = data.get("data", {}).get("channel")
        if not channel_info:
            raise RuntimeError("Buffer Channel তথ্য পাওয়া যায়নি!")

        logger.info(f"✅ Buffer LinkedIn Channel Verified: {channel_info.get('name')} ({channel_info.get('service')})")
        return channel_info

    def publish_post(self, text: str, image_url: Optional[str] = None, mode: str = "shareNow") -> str:
        """
        Publishes a post via Buffer to LinkedIn.
        - mode='shareNow' publishes immediately.
        - mode='addToQueue' adds to the queue.
        Returns the post ID.
        """
        if not self.api_key or not self.channel_id:
            raise ValueError("Buffer API Key অথবা Channel ID মিসিং!")

        mutation = """
        mutation CreatePost($input: CreatePostInput!) {
            createPost(input: $input) {
                ... on PostActionSuccess {
                    post {
                        id
                        status
                    }
                }
                ... on MutationError {
                    message
                }
            }
        }
        """

        input_data: Dict[str, Any] = {
            "channelId": self.channel_id,
            "text": text,
            "schedulingType": "automatic",
            "mode": mode
        }

        if image_url:
            input_data["assets"] = [{"image": {"url": image_url}}]

        payload = {
            "query": mutation,
            "variables": {"input": input_data}
        }

        res = requests.post(BUFFER_GRAPHQL_ENDPOINT, headers=self.headers, json=payload, timeout=30)
        if res.status_code != 200:
            raise RuntimeError(f"Buffer API Call Failed (Status {res.status_code}): {res.text}")

        result = res.json()
        if "errors" in result:
            raise RuntimeError(f"Buffer GraphQL Mutation Failed: {result['errors']}")

        create_post_data = result.get("data", {}).get("createPost", {})
        if "message" in create_post_data:
            raise RuntimeError(f"Buffer Post Creation Error: {create_post_data['message']}")

        post = create_post_data.get("post", {})
        post_id = post.get("id", "buffer_published")
        logger.info(f"🎉 Buffer Post Published Successfully! Post ID: {post_id}")
        return str(post_id)
