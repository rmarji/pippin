"""X (Twitter) API integration skill."""

import logging
import base64
import aiohttp
import os
from typing import Dict, Any, Optional, List
from framework.composio_integration import composio_manager
from pathlib import Path

logger = logging.getLogger(__name__)


class XAPIError(Exception):
    """Custom exception for X API errors"""
    pass


class XAPISkill:
    """Skill for interacting with X (Twitter) API via Composio."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize skill configuration."""
        self.config = config
        self.enabled = config.get("enabled", False)
        self.rate_limit = config.get("rate_limit", 100)
        self.cooldown_period = config.get("cooldown_period", 300)
        self.posts_count = 0
        self.twitter_username = config.get("twitter_username", "YourUserName")  # Get from config
        
        # Create storage directory if it doesn't exist
        # Get the project root directory (2 levels up from this file)
        current_file = Path(__file__)
        project_root = current_file.parent.parent
        self.storage_path = project_root / "storage" / "images"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Image storage path: {self.storage_path}")
        
        # Composio action names
        self.post_action = "TWITTER_CREATION_OF_A_POST"
        self.media_upload_action = "TWITTER_MEDIA_UPLOAD_MEDIA"

        if not self.twitter_username:
            logger.warning("No twitter_username provided in config")

    def can_post(self) -> bool:
        """Check if posting is allowed based on rate limits."""
        return self.enabled and self.posts_count < self.rate_limit

    async def upload_media(self, media_url: str) -> Optional[str]:
        """
        Download image from URL and upload to Twitter via Composio.
        Returns media ID if successful, None otherwise.
        """
        local_path = None
        try:
            logger.info(f"Downloading media from URL: {media_url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(media_url) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to download image from {media_url}: {response.status}")
                        return None
                    
                    # Extract filename and create local path
                    filename = media_url.split('/')[-1].split('?')[0] or 'image.png'
                    local_path = self.storage_path / filename
                    
                    # Save the file locally
                    image_data = await response.read()
                    with open(local_path, 'wb') as f:
                        f.write(image_data)
                    
                    logger.info(f"Saved image to {local_path}")
                    
                    # Upload to Twitter via Composio
                    logger.info(f"Uploading media to Twitter")
                    upload_response = composio_manager._toolset.execute_action(
                        action=self.media_upload_action,
                        params={
                            "media": str(local_path)  # Just pass the file path as a string
                        },
                        entity_id="MyDigitalBeing"
                    )
                
                if upload_response.get("successful"):
                    media_id = upload_response.get("data", {}).get("media_id")
                    if media_id:
                        logger.info(f"Successfully uploaded image to Twitter, media_id: {media_id}")
                        return media_id
                
                logger.warning(f"Failed to upload image to Twitter: {upload_response.get('error', 'Unknown error')}")
                return None
                    
        except Exception as e:
            logger.error(f"Error uploading image to Twitter: {e}", exc_info=True)
            return None
        
        finally:
            # Clean up the temporary file
            if local_path and local_path.exists():
                try:
                    local_path.unlink()
                    logger.info(f"Cleaned up temporary file: {local_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {local_path}: {e}")

    async def post_tweet(self, text: str, media_urls: List[str] = None) -> Dict[str, Any]:
        """
        Post a tweet with optional media attachments using Composio.
        Handles media upload internally if media_urls are provided.
        Returns dict with success status and tweet data.
        """
        if not self.can_post():
            return {"success": False, "error": "Rate limit exceeded or skill disabled"}

        try:
            # First handle media uploads if any
            media_ids = []
            if media_urls:
                for url in media_urls:
                    media_id = await self.upload_media(url)
                    if media_id:
                        media_ids.append(media_id)

            # Now post the tweet with any media IDs we collected
            logger.info(
                f"Posting tweet via Composio action='{self.post_action}', "
                f"text='{text[:50]}...', media_count={len(media_ids)}"
            )

            params = {"text": text}
            if media_ids:
                params["media__media__ids"] = media_ids

            response = composio_manager._toolset.execute_action(
                action=self.post_action,
                params=params,
                entity_id="MyDigitalBeing",
            )

            # The actual success key is "successfull" (with 2 Ls)
            success_val = response.get("success", response.get("successfull"))
            if success_val:
                data_section = response.get("data", {})
                nested_data = data_section.get("data", {})
                tweet_id = nested_data.get("id")
                
                tweet_link = (
                    f"https://twitter.com/{self.twitter_username}/status/{tweet_id}"
                    if tweet_id else None
                )
                
                self.posts_count += 1
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "content": text,
                    "tweet_link": tweet_link,
                    "media_count": len(media_ids)
                }
            else:
                error_msg = response.get("error", "Unknown or missing success key")
                logger.error(f"Tweet posting failed: {error_msg}")
                return {"success": False, "error": error_msg}

        except Exception as e:
            logger.error(f"Failed to post tweet: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def reset_counts(self):
        """Reset the post counter."""
        self.posts_count = 0
