"""Activity for performing comprehensive market research."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from framework.activity_decorator import activity, ActivityBase, ActivityResult
from framework.api_management import api_manager

logger = logging.getLogger(__name__)


@activity(
    name="market_research",
    energy_cost=0.5,
    cooldown=3600,  # 1 hour
    required_skills=["market_research"],
)
class MarketResearchActivity(ActivityBase):
    def __init__(self):
        super().__init__()
        self.target_markets = [
            "saas",
            "e-commerce",
            "digital_products",
            "consulting",
            "mobile_apps"
        ]
        self.focus_areas = [
            "emerging trends",
            "market size",
            "growth opportunities",
            "competitive landscape"
        ]

    async def execute(self, shared_data) -> ActivityResult:
        """Execute market research activity."""
        try:
            logger.info("Starting market research activity")
            
            # Initialize market research skill
            api_key = api_manager.get_api_key("linkup")
            if not api_key:
                return ActivityResult(
                    success=False,
                    error="Linkup API key not configured"
                )

            from my_digital_being.skills.skill_market_research import MarketResearchSkill
            market_skill = MarketResearchSkill(api_key)
            
            # Gather market data
            market_data = await self._gather_market_data(market_skill)
            
            # Analyze opportunities
            opportunities = self._analyze_opportunities(market_data)
            
            # Store results in memory
            research_data = {
                "timestamp": datetime.now().isoformat(),
                "market_data": market_data,
                "opportunities": opportunities
            }
            
            shared_data.set("memory", "latest_market_research", research_data)
            
            return ActivityResult(
                success=True,
                data=research_data,
                metadata={
                    "markets_analyzed": self.target_markets,
                    "timestamp": research_data["timestamp"]
                }
            )

        except Exception as e:
            logger.error(f"Failed to complete market research: {e}")
            return ActivityResult(success=False, error=str(e))

    async def _gather_market_data(self, market_skill) -> Dict[str, Any]:
        """Gather market data from various sources."""
        market_data = {
            "news": [],
            "trends": [],
            "competitors": []
        }
        
        try:
            # Get market news
            for market in self.target_markets:
                query = f"latest {market} market trends business opportunities"
                news = await market_skill.search_market_news(query)
                for item in news:
                    item["market"] = market
                market_data["news"].extend(news)
            
            # Get market trends
            for market in self.target_markets:
                trends = await market_skill.analyze_market_trends(
                    market,
                    self.focus_areas
                )
                if trends:
                    market_data["trends"].append(trends)
            
            # Get competitor analysis
            competitor_types = ["established", "startup", "emerging"]
            for market in self.target_markets:
                competitors = await market_skill.research_competitors(
                    market,
                    competitor_types
                )
                if competitors:
                    market_data["competitors"].append(competitors)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error gathering market data: {e}")
            return market_data

    def _analyze_opportunities(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze data to identify concrete opportunities."""
        opportunities = []
        
        if not market_data:
            return opportunities
            
        # Analyze news for opportunities
        if "news" in market_data:
            for news_item in market_data["news"]:
                opportunity = {
                    "market": news_item["market"],
                    "type": "news_based",
                    "title": news_item["title"],
                    "insight": news_item["summary"],
                    "source_url": news_item["url"],
                    "requirements": {
                        "skills": [],
                        "initial_investment": "Unknown",
                        "time_to_market": "Unknown"
                    },
                    "risks": [],
                    "next_steps": []
                }
                opportunities.append(opportunity)
        
        # Add trend-based opportunities
        if "trends" in market_data:
            for trend_data in market_data["trends"]:
                market = trend_data.get("market", "")
                for trend in trend_data.get("trends", []):
                    for insight in trend.get("insights", []):
                        opportunity = {
                            "market": market,
                            "type": "trend_based",
                            "title": insight["title"],
                            "insight": insight["summary"],
                            "source": insight["source"],
                            "focus_area": trend["focus_area"],
                            "requirements": {
                                "skills": [],
                                "initial_investment": "Unknown",
                                "time_to_market": "Unknown"
                            },
                            "risks": [],
                            "next_steps": []
                        }
                        opportunities.append(opportunity)
        
        return opportunities