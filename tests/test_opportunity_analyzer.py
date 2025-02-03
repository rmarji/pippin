"""Tests for the opportunity analyzer activity."""

import pytest
from datetime import datetime
from my_digital_being.activities.activity_opportunity_analyzer import OpportunityAnalyzerActivity
from my_digital_being.framework.shared_data import SharedData


@pytest.fixture
def mock_market_research():
    return {
        "timestamp": datetime.now().isoformat(),
        "opportunities": [
            {
                "market": "saas",
                "type": "trend_based",
                "title": "AI-Powered Analytics Platform",
                "insight": "Growing demand for AI analytics in business",
                "market_size": "$5 billion",
                "growth_rate": "25% CAGR",
                "requirements": {
                    "skills": ["AI/ML", "Cloud Architecture"],
                    "time_to_market": "6 months"
                },
                "risks": ["Technical complexity", "Market competition"]
            },
            {
                "market": "digital_products",
                "type": "news_based",
                "title": "Online Course Platform",
                "insight": "Surge in remote learning demand",
                "market_size": "$350 million",
                "growth_rate": "15% CAGR",
                "requirements": {
                    "skills": ["Web Development"],
                    "time_to_market": "3 months"
                },
                "risks": ["Market saturation"]
            }
        ]
    }


@pytest.fixture
def mock_shared_data(mock_market_research):
    shared_data = SharedData()
    shared_data.initialize()
    shared_data.set("memory", "latest_market_research", mock_market_research)
    return shared_data


@pytest.mark.asyncio
async def test_opportunity_analyzer_execution(mock_shared_data):
    activity = OpportunityAnalyzerActivity()
    
    result = await activity.execute(mock_shared_data)
    
    assert result.success
    assert "opportunities" in result.data
    assert "evaluation_criteria" in result.data
    assert "timestamp" in result.data


@pytest.mark.asyncio
async def test_opportunity_scoring(mock_shared_data):
    activity = OpportunityAnalyzerActivity()
    
    result = await activity.execute(mock_shared_data)
    
    opportunities = result.data["opportunities"]
    for opportunity in opportunities:
        assert "scores" in opportunity
        assert "market_potential" in opportunity["scores"]
        assert "feasibility" in opportunity["scores"]
        assert "risk_level" in opportunity["scores"]
        assert "profitability" in opportunity["scores"]
        assert "overall_score" in opportunity
        assert 0 <= opportunity["overall_score"] <= 1


@pytest.mark.asyncio
async def test_opportunity_prioritization(mock_shared_data):
    activity = OpportunityAnalyzerActivity()
    
    result = await activity.execute(mock_shared_data)
    
    opportunities = result.data["opportunities"]
    assert any(opp.get("priority") == "High" for opp in opportunities)
    
    # Verify opportunities are sorted by score
    scores = [opp["overall_score"] for opp in opportunities]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.asyncio
async def test_action_plan_generation(mock_shared_data):
    activity = OpportunityAnalyzerActivity()
    
    result = await activity.execute(mock_shared_data)
    
    opportunities = result.data["opportunities"]
    for opportunity in opportunities:
        assert "action_plan" in opportunity
        assert "immediate_actions" in opportunity["action_plan"]
        assert "required_resources" in opportunity["action_plan"]
        
        if opportunity["priority"] == "High":
            assert "milestones" in opportunity["action_plan"]


@pytest.mark.asyncio
async def test_storage_in_memory(mock_shared_data):
    activity = OpportunityAnalyzerActivity()
    
    await activity.execute(mock_shared_data)
    
    stored_analysis = mock_shared_data.get("memory", "latest_opportunity_analysis")
    assert stored_analysis is not None
    assert "opportunities" in stored_analysis
    assert "evaluation_criteria" in stored_analysis
    assert "timestamp" in stored_analysis


@pytest.mark.asyncio
async def test_no_market_research_handling():
    activity = OpportunityAnalyzerActivity()
    empty_shared_data = SharedData()
    empty_shared_data.initialize()
    
    result = await activity.execute(empty_shared_data)
    
    assert not result.success
    assert "No market research data available" in result.error