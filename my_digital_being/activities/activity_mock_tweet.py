"""Activity for simulating tweet posting without actual Twitter integration."""

import logging
from typing import Dict, Any
from my_digital_being.framework.activity_decorator import activity, ActivityBase, ActivityResult

logger = logging.getLogger(__name__)


@activity(
    name="mock_tweet",
    energy_cost=0.1,
    cooldown=300,  # 5 minutes
    required_skills=[],  # No special skills needed since it's just mocking
)
class MockTweetActivity(ActivityBase):
    def __init__(self):
        super().__init__()
        self.max_tweet_length = 280

    async def execute(self, shared_data) -> ActivityResult:
        """Execute the mock tweet activity."""
        try:
            logger.info("Starting mock tweet activity")

            # Generate a mock tweet (could be based on recent activities or news)
            tweet_content = await self._generate_tweet_content(shared_data)
            
            if len(tweet_content) > self.max_tweet_length:
                tweet_content = tweet_content[:self.max_tweet_length-3] + "..."

            logger.info(f"Mock tweet created: {tweet_content}")
            
            # Store in memory for potential future reference
            from datetime import datetime
            shared_data.set("memory", "latest_mock_tweet", {
                "content": tweet_content,
                "timestamp": datetime.now().isoformat()
            })

            return ActivityResult(
                success=True,
                data={"content": tweet_content},
                metadata={"length": len(tweet_content)}
            )

        except Exception as e:
            logger.error(f"Failed to create mock tweet: {e}")
            return ActivityResult(success=False, error=str(e))

    async def _generate_tweet_content(self, shared_data) -> str:
        """Generate tweet content based on recent activities."""
        # Try to get recent news first
        latest_news = shared_data.get("memory", "latest_news", [])
        if latest_news and isinstance(latest_news, list) and len(latest_news) > 0:
            article = latest_news[0]  # Get most recent article
            return f"📰 Latest Update: {article.get('title', 'Interesting news')} #News"
        
        # Fallback content if no news available
        return "🤖 Just another day of digital being activities! #DigitalLife"