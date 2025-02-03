"""Activity for evaluating money-making opportunities using market research."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from framework.activity_decorator import activity, ActivityBase, ActivityResult
from framework.api_management import api_manager

logger = logging.getLogger(__name__)


@activity(
    name="money_evaluation",
    energy_cost=0.6,
    cooldown=7200,  # 2 hours
    required_skills=["market_research", "lite_llm"],
)
class MoneyEvaluationActivity(ActivityBase):
    def __init__(self):
        super().__init__()
        self.evaluation_criteria = {
            "market_potential": {
                "weight": 0.3,
                "factors": ["market_size", "growth_rate", "competition"]
            },
            "feasibility": {
                "weight": 0.25,
                "factors": ["technical_complexity", "resource_requirements", "time_to_market"]
            },
            "risk_level": {
                "weight": 0.25,
                "factors": ["market_risks", "technical_risks", "regulatory_risks"]
            },
            "profitability": {
                "weight": 0.2,
                "factors": ["revenue_potential", "cost_structure", "scalability"]
            }
        }

    async def execute(self, shared_data) -> ActivityResult:
        """Execute money evaluation activity."""
        try:
            logger.info("Starting money evaluation activity")
            
            # Initialize market research skill
            api_key = api_manager.get_api_key("linkup")
            if not api_key:
                return ActivityResult(
                    success=False,
                    error="Linkup API key not configured"
                )

            from my_digital_being.skills.skill_market_research import MarketResearchSkill
            market_skill = MarketResearchSkill(api_key)
            
            # Get latest market research or perform new research
            market_data = await self._get_market_data(market_skill, shared_data)
            
            # Analyze opportunities
            opportunities = await self._analyze_opportunities(market_data)
            
            # Generate detailed evaluations
            evaluations = self._evaluate_opportunities(opportunities)
            
            # Store results
            evaluation_result = {
                "timestamp": datetime.now().isoformat(),
                "market_data": market_data,
                "opportunities": opportunities,
                "evaluations": evaluations,
                "criteria": self.evaluation_criteria
            }
            
            shared_data.set("memory", "latest_money_evaluation", evaluation_result)
            
            return ActivityResult(
                success=True,
                data=evaluation_result,
                metadata={
                    "opportunities_evaluated": len(opportunities),
                    "timestamp": evaluation_result["timestamp"]
                }
            )

        except Exception as e:
            logger.error(f"Failed to evaluate money-making opportunities: {e}")
            return ActivityResult(success=False, error=str(e))

    async def _get_market_data(self, market_skill, shared_data) -> Dict[str, Any]:
        """Get market data from memory or fetch new data."""
        latest_research = shared_data.get("memory", "latest_market_research")
        
        if latest_research and self._is_data_fresh(latest_research.get("timestamp")):
            return latest_research.get("market_data", {})
            
        # Perform new market research
        market_data = {
            "news": [],
            "trends": [],
            "competitors": []
        }
        
        try:
            # Focus on business and technology sectors
            sectors = ["business", "technology", "startup", "investment"]
            for sector in sectors:
                query = f"{sector} opportunities market analysis"
                news = await market_skill.search_market_news(query)
                for item in news:
                    item["sector"] = sector
                market_data["news"].extend(news)
            
            # Analyze market trends
            focus_areas = ["emerging markets", "digital transformation", "consumer behavior"]
            for sector in sectors:
                trends = await market_skill.analyze_market_trends(sector, focus_areas)
                if trends:
                    market_data["trends"].append(trends)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error gathering market data: {e}")
            return market_data

    def _is_data_fresh(self, timestamp: str, max_age_hours: int = 24) -> bool:
        """Check if data is fresh enough to use."""
        if not timestamp:
            return False
            
        try:
            data_time = datetime.fromisoformat(timestamp)
            age = datetime.now() - data_time
            return age.total_seconds() < (max_age_hours * 3600)
        except ValueError:
            return False

    async def _analyze_opportunities(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze market data to identify opportunities."""
        opportunities = []
        
        if not market_data:
            return opportunities
            
        # Extract opportunities from news
        if "news" in market_data:
            for news_item in market_data["news"]:
                opportunity = {
                    "type": "news_based",
                    "sector": news_item.get("sector", "general"),
                    "title": news_item["title"],
                    "insight": news_item["summary"],
                    "source": news_item["source"],
                    "url": news_item.get("url", ""),
                    "requirements": {
                        "skills": [],
                        "initial_investment": "Unknown",
                        "time_to_market": "Unknown"
                    }
                }
                opportunities.append(opportunity)
        
        # Extract opportunities from trends
        if "trends" in market_data:
            for trend_data in market_data["trends"]:
                for trend in trend_data.get("trends", []):
                    for insight in trend.get("insights", []):
                        opportunity = {
                            "type": "trend_based",
                            "sector": trend_data.get("market", "general"),
                            "title": insight["title"],
                            "insight": insight["summary"],
                            "source": insight["source"],
                            "focus_area": trend.get("focus_area", ""),
                            "requirements": {
                                "skills": [],
                                "initial_investment": "Unknown",
                                "time_to_market": "Unknown"
                            }
                        }
                        opportunities.append(opportunity)
        
        return opportunities

    def _evaluate_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate each opportunity against criteria."""
        evaluations = []
        
        for opportunity in opportunities:
            scores = {
                "market_potential": self._evaluate_market_potential(opportunity),
                "feasibility": self._evaluate_feasibility(opportunity),
                "risk_level": self._evaluate_risks(opportunity),
                "profitability": self._evaluate_profitability(opportunity)
            }
            
            # Calculate weighted score
            total_score = sum(
                score * self.evaluation_criteria[criterion]["weight"]
                for criterion, score in scores.items()
            )
            
            evaluation = {
                "opportunity": opportunity,
                "scores": scores,
                "overall_score": round(total_score, 2),
                "priority": self._get_priority_level(total_score),
                "recommendations": self._generate_recommendations(opportunity, scores)
            }
            
            evaluations.append(evaluation)
        
        # Sort by overall score
        return sorted(evaluations, key=lambda x: x["overall_score"], reverse=True)

    def _evaluate_market_potential(self, opportunity: Dict[str, Any]) -> float:
        """Evaluate market potential on a scale of 0-1."""
        score = 0.5  # Base score
        
        # Adjust based on sector
        high_potential_sectors = ["technology", "digital_transformation", "ai", "sustainability"]
        if any(sector in opportunity.get("sector", "").lower() for sector in high_potential_sectors):
            score += 0.2
            
        # Adjust based on insight content
        insight = opportunity.get("insight", "").lower()
        if "growing market" in insight or "high demand" in insight:
            score += 0.1
        if "emerging" in insight or "innovative" in insight:
            score += 0.1
            
        return min(1.0, score)

    def _evaluate_feasibility(self, opportunity: Dict[str, Any]) -> float:
        """Evaluate implementation feasibility on a scale of 0-1."""
        score = 0.5  # Base score
        
        # Adjust based on sector
        digital_sectors = ["software", "digital", "online", "saas"]
        if any(sector in opportunity.get("sector", "").lower() for sector in digital_sectors):
            score += 0.2  # Digital typically easier to implement
            
        # Adjust based on requirements
        reqs = opportunity.get("requirements", {})
        if len(reqs.get("skills", [])) <= 2:  # Few skills needed
            score += 0.1
            
        return min(1.0, score)

    def _evaluate_risks(self, opportunity: Dict[str, Any]) -> float:
        """Evaluate risk level on a scale of 0-1 (higher is better/lower risk)."""
        score = 0.5  # Base score
        
        # Adjust based on sector stability
        stable_sectors = ["essential_services", "b2b", "enterprise"]
        if any(sector in opportunity.get("sector", "").lower() for sector in stable_sectors):
            score += 0.2
            
        # Adjust based on insight content
        insight = opportunity.get("insight", "").lower()
        if "proven" in insight or "established" in insight:
            score += 0.1
        if "risky" in insight or "uncertain" in insight:
            score -= 0.1
            
        return min(1.0, max(0.0, score))

    def _evaluate_profitability(self, opportunity: Dict[str, Any]) -> float:
        """Evaluate potential profitability on a scale of 0-1."""
        score = 0.5  # Base score
        
        # Adjust based on sector
        high_margin_sectors = ["saas", "digital_products", "consulting"]
        if any(sector in opportunity.get("sector", "").lower() for sector in high_margin_sectors):
            score += 0.2
            
        # Adjust based on insight content
        insight = opportunity.get("insight", "").lower()
        if "profitable" in insight or "revenue" in insight:
            score += 0.1
        if "competitive" in insight or "saturated" in insight:
            score -= 0.1
            
        return min(1.0, max(0.0, score))

    def _get_priority_level(self, score: float) -> str:
        """Determine priority level based on score."""
        if score >= 0.8:
            return "High"
        elif score >= 0.6:
            return "Medium"
        else:
            return "Low"

    def _generate_recommendations(
        self, opportunity: Dict[str, Any], scores: Dict[str, float]
    ) -> List[str]:
        """Generate specific recommendations based on evaluation."""
        recommendations = []
        
        # Market potential recommendations
        if scores["market_potential"] < 0.6:
            recommendations.append(
                "Conduct deeper market research to validate demand and identify specific niches"
            )
            
        # Feasibility recommendations
        if scores["feasibility"] < 0.6:
            recommendations.append(
                "Break down implementation into smaller phases to reduce complexity"
            )
            
        # Risk recommendations
        if scores["risk_level"] < 0.6:
            recommendations.append(
                "Develop risk mitigation strategies and identify potential pivots"
            )
            
        # Profitability recommendations
        if scores["profitability"] < 0.6:
            recommendations.append(
                "Explore additional revenue streams and optimization opportunities"
            )
            
        # Add general recommendations
        recommendations.extend([
            "Create detailed implementation timeline",
            "Identify key partnerships or resources needed",
            "Define clear success metrics"
        ])
        
        return recommendations