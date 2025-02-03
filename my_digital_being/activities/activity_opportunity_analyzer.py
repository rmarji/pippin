"""Activity for analyzing and prioritizing business opportunities."""

import logging
from typing import Dict, Any, List
from datetime import datetime
from framework.activity_decorator import activity, ActivityBase, ActivityResult

logger = logging.getLogger(__name__)


@activity(
    name="opportunity_analyzer",
    energy_cost=0.4,
    cooldown=1800,  # 30 minutes
    required_skills=["openai_chat"],
)
class OpportunityAnalyzerActivity(ActivityBase):
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
        """Execute opportunity analysis."""
        try:
            logger.info("Starting opportunity analysis")
            
            # Get latest market research
            market_research = shared_data.get("memory", "latest_market_research")
            if not market_research:
                return ActivityResult(
                    success=False,
                    error="No market research data available"
                )

            # Analyze opportunities
            analyzed_opportunities = await self._analyze_opportunities(
                market_research.get("opportunities", [])
            )
            
            # Prioritize opportunities
            prioritized_opportunities = self._prioritize_opportunities(
                analyzed_opportunities
            )
            
            # Generate action plans
            opportunities_with_plans = self._generate_action_plans(
                prioritized_opportunities
            )
            
            # Store results
            analysis_result = {
                "timestamp": datetime.now().isoformat(),
                "opportunities": opportunities_with_plans,
                "evaluation_criteria": self.evaluation_criteria
            }
            
            shared_data.set("memory", "latest_opportunity_analysis", analysis_result)
            
            return ActivityResult(
                success=True,
                data=analysis_result,
                metadata={
                    "opportunities_analyzed": len(analyzed_opportunities),
                    "timestamp": analysis_result["timestamp"]
                }
            )

        except Exception as e:
            logger.error(f"Failed to analyze opportunities: {e}")
            return ActivityResult(success=False, error=str(e))

    async def _analyze_opportunities(
        self, opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Add detailed analysis to each opportunity."""
        analyzed_opportunities = []
        
        for opportunity in opportunities:
            analysis = {
                **opportunity,
                "scores": {
                    "market_potential": self._evaluate_market_potential(opportunity),
                    "feasibility": self._evaluate_feasibility(opportunity),
                    "risk_level": self._evaluate_risks(opportunity),
                    "profitability": self._evaluate_profitability(opportunity)
                }
            }
            
            # Calculate overall score
            total_score = sum(
                score * self.evaluation_criteria[criterion]["weight"]
                for criterion, score in analysis["scores"].items()
            )
            
            analysis["overall_score"] = round(total_score, 2)
            analyzed_opportunities.append(analysis)
            
        return analyzed_opportunities

    def _evaluate_market_potential(self, opportunity: Dict[str, Any]) -> float:
        """Evaluate market potential on a scale of 0-1."""
        # This could be expanded with more sophisticated market analysis
        base_score = 0.7  # Default optimistic score
        
        # Adjust based on market size if available
        if "market_size" in opportunity:
            size_str = opportunity["market_size"]
            if "trillion" in size_str.lower():
                base_score += 0.2
            elif "billion" in size_str.lower():
                base_score += 0.1
                
        # Adjust based on growth rate
        if "growth_rate" in opportunity:
            growth_str = opportunity["growth_rate"]
            if "%" in growth_str:
                try:
                    rate = float(growth_str.split("%")[0])
                    if rate > 20:
                        base_score += 0.1
                    elif rate > 10:
                        base_score += 0.05
                except ValueError:
                    pass
                    
        return min(1.0, base_score)

    def _evaluate_feasibility(self, opportunity: Dict[str, Any]) -> float:
        """Evaluate implementation feasibility on a scale of 0-1."""
        base_score = 0.6  # Default moderate score
        
        requirements = opportunity.get("requirements", {})
        
        # Adjust based on required skills
        if "skills" in requirements:
            skills_needed = len(requirements["skills"])
            if skills_needed <= 2:
                base_score += 0.2
            elif skills_needed <= 4:
                base_score += 0.1
                
        # Adjust based on time to market
        time_to_market = requirements.get("time_to_market", "Unknown")
        if "month" in str(time_to_market).lower():
            base_score += 0.1
            
        return min(1.0, base_score)

    def _evaluate_risks(self, opportunity: Dict[str, Any]) -> float:
        """Evaluate risk level on a scale of 0-1 (higher is better/lower risk)."""
        base_score = 0.5  # Default moderate risk
        
        risks = opportunity.get("risks", [])
        
        # Fewer risks is better
        if len(risks) <= 2:
            base_score += 0.3
        elif len(risks) <= 4:
            base_score += 0.1
            
        return min(1.0, base_score)

    def _evaluate_profitability(self, opportunity: Dict[str, Any]) -> float:
        """Evaluate potential profitability on a scale of 0-1."""
        base_score = 0.5  # Default moderate score
        
        # This could be enhanced with actual financial modeling
        if "market" in opportunity:
            if opportunity["market"] in ["saas", "digital_products"]:
                base_score += 0.2  # Higher margins in these markets
                
        return min(1.0, base_score)

    def _prioritize_opportunities(
        self, analyzed_opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sort opportunities by overall score and add priority levels."""
        # Sort by overall score
        sorted_opportunities = sorted(
            analyzed_opportunities,
            key=lambda x: x["overall_score"],
            reverse=True
        )
        
        # Add priority levels
        for idx, opportunity in enumerate(sorted_opportunities):
            if idx < len(sorted_opportunities) * 0.2:  # Top 20%
                opportunity["priority"] = "High"
            elif idx < len(sorted_opportunities) * 0.5:  # Next 30%
                opportunity["priority"] = "Medium"
            else:  # Bottom 50%
                opportunity["priority"] = "Low"
                
        return sorted_opportunities

    def _generate_action_plans(
        self, opportunities: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate concrete action plans for each opportunity."""
        for opportunity in opportunities:
            if opportunity["priority"] == "High":
                opportunity["action_plan"] = self._create_detailed_plan(opportunity)
            else:
                opportunity["action_plan"] = self._create_basic_plan(opportunity)
                
        return opportunities

    def _create_detailed_plan(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Create a detailed action plan for high-priority opportunities."""
        return {
            "immediate_actions": [
                "Conduct detailed market analysis",
                "Identify potential first customers",
                "Draft initial business plan",
                "Research regulatory requirements"
            ],
            "required_resources": {
                "estimated_budget": "TBD based on market research",
                "key_skills": opportunity.get("requirements", {}).get("skills", []),
                "timeline": "90 days initial phase"
            },
            "milestones": [
                {
                    "name": "Market Validation",
                    "timeline": "30 days",
                    "success_criteria": [
                        "Identified 10+ potential customers",
                        "Completed competitor analysis",
                        "Defined unique value proposition"
                    ]
                },
                {
                    "name": "MVP Planning",
                    "timeline": "60 days",
                    "success_criteria": [
                        "Detailed technical requirements",
                        "Resource plan",
                        "Initial cost estimates"
                    ]
                }
            ]
        }

    def _create_basic_plan(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic action plan for medium/low-priority opportunities."""
        return {
            "immediate_actions": [
                "Monitor market conditions",
                "Track competitor activities",
                "Identify potential entry points"
            ],
            "required_resources": {
                "estimated_budget": "Minimal - monitoring only",
                "key_skills": ["Market research"],
                "timeline": "Ongoing monitoring"
            }
        }