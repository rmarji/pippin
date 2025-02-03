"""Skill for performing market research using the Linkup API."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from linkup import LinkupClient

logger = logging.getLogger(__name__)


class MarketResearchSkill:
    """Skill for performing market research and analysis."""

    def __init__(self, api_key: str):
        self.client = LinkupClient(api_key=api_key)
        self.default_depth = "standard"
        self.default_output_type = "searchResults"

    async def search_market_news(
        self, query: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for market-related news and trends."""
        try:
            response = self.client.search(
                query=query,
                depth=self.default_depth,
                output_type=self.default_output_type
            )

            if not response or "results" not in response:
                logger.warning(f"No results found for query: {query}")
                return []

            news_items = []
            for item in response["results"][:max_results]:
                news_items.append({
                    "title": item.get("title", ""),
                    "summary": item.get("snippet", ""),
                    "url": item.get("link", ""),
                    "source": item.get("source", ""),
                    "timestamp": datetime.now().isoformat()
                })

            return news_items

        except Exception as e:
            logger.error(f"Error searching market news: {e}")
            return []

    async def analyze_market_trends(
        self, market: str, focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Analyze trends for a specific market."""
        try:
            trends_data = []
            
            for area in focus_areas:
                query = f"{market} {area} trends analysis market size growth"
                results = await self.search_market_news(query, max_results=3)
                
                if results:
                    trends_data.append({
                        "focus_area": area,
                        "insights": [
                            {
                                "title": item["title"],
                                "summary": item["summary"],
                                "source": item["source"]
                            }
                            for item in results
                        ]
                    })

            return {
                "market": market,
                "trends": trends_data,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            return {}

    async def research_competitors(
        self, market: str, competitor_types: List[str]
    ) -> Dict[str, Any]:
        """Research competitors in a specific market."""
        try:
            competitor_data = []
            
            for comp_type in competitor_types:
                query = f"top {market} {comp_type} companies competitors analysis"
                results = await self.search_market_news(query, max_results=5)
                
                if results:
                    competitor_data.append({
                        "segment": comp_type,
                        "competitors": [
                            {
                                "name": self._extract_company_name(item["title"]),
                                "description": item["summary"],
                                "source": item["source"]
                            }
                            for item in results
                        ]
                    })

            return {
                "market": market,
                "segments": competitor_data,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error researching competitors: {e}")
            return {}

    def _extract_company_name(self, title: str) -> str:
        """Extract company name from article title (placeholder implementation)."""
        # This could be enhanced with NLP for better company name extraction
        words = title.split()
        if len(words) > 3:
            return " ".join(words[:3]) + "..."
        return title