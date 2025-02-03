"""Activity for fetching news using web scraping."""

import logging
from typing import Dict, Any, List
from framework.activity_decorator import activity, ActivityBase, ActivityResult

logger = logging.getLogger(__name__)


@activity(
    name="fetch_news",
    energy_cost=0.3,
    cooldown=1800,  # 30 minutes
    required_skills=["web_scraping"],
)
class FetchNewsActivity(ActivityBase):
    def __init__(self):
        super().__init__()
        self.topics = ["technology", "science", "art"]
        self.max_articles = 5

    async def execute(self, shared_data) -> ActivityResult:
        """Execute the news fetching activity."""
        try:
            logger.info("Starting news fetch activity")

            # Simulate fetching news
            articles = await self._fetch_articles()

            # Store articles in shared data
            shared_data.set("memory", "latest_news", articles)

            logger.info(f"Successfully fetched {len(articles)} articles")
            return ActivityResult(
                success=True,
                data={"articles": articles, "count": len(articles)},
                metadata={"topics": self.topics, "max_articles": self.max_articles},
            )

        except Exception as e:
            logger.error(f"Failed to fetch news: {e}")
            return ActivityResult(success=False, error=str(e))

    async def _fetch_articles(self) -> List[Dict[str, Any]]:
        from linkup import LinkupClient

        client = LinkupClient(api_key="6cc75ac1-254c-43b1-9c8f-10ab869e307b")
        try:
            logger.info("Using LinkupClient to fetch news")
            response = client.search(
                query="latest technology news",
                depth="standard",
                output_type="searchResults"
            )
            articles = []
            results = response.get("results", [])
            for idx, result in enumerate(results[: self.max_articles]):
                topic = "general"
                articles.append(
                    {
                        "title": result.get("title", f"Article {idx + 1}"),
                        "topic": topic,
                        "summary": result.get("snippet", "No summary available"),
                        "url": result.get("link", "https://example.com"),
                    }
                )
            logger.info(f"Fetched {len(articles)} articles via LinkupClient")
            return articles
        except Exception as e:
            logger.error(f"LinkupClient search failed: {e}")
            return []
