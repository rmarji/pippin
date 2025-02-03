"""Tests for the money evaluation activity."""

import pytest
from datetime import datetime, timedelta
from my_digital_being.activities.activity_money_evaluation import MoneyEvaluationActivity
from my_digital_being.framework.shared_data import SharedData


@pytest.fixture
def mock_market_data():
    return {
        "news": [
            {
                "sector": "technology",
                "title": "AI Market Growth",
                "summary": "Growing market for AI solutions",
                "source": "Tech News",
                "url": "https://example.com/ai-growth"
            },
            {
                "sector": "saas",
                "title": "SaaS Trends 2025",
                "summary": "Emerging SaaS opportunities",
                "source": "Business Weekly",
                "url": "https://example.com/saas-trends"
            }
        ],
        "trends": [
            {
                "market": "technology",
                "trends": [
                    {
                        "focus_area": "emerging markets",
                        "insights": [
                            {
                                "title": "Cloud Computing Growth",
                                "summary": "Rapid adoption of cloud services",
                                "source": "Market Research"
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_shared_data(mock_market_data):
    shared_data = SharedData()
    shared_data.initialize()
    
    # Add mock market research data
    research_data = {
        "timestamp": datetime.now().isoformat(),
        "market_data": mock_market_data
    }
    shared_data.set("memory", "latest_market_research", research_data)
    
    return shared_data


@pytest.mark.asyncio
async def test_money_evaluation_execution(mock_shared_data):
    activity = MoneyEvaluationActivity()
    
    result = await activity.execute(mock_shared_data)
    
    assert result.success
    assert "market_data" in result.data
    assert "opportunities" in result.data
    assert "evaluations" in result.data
    assert "criteria" in result.data
    assert "timestamp" in result.data


@pytest.mark.asyncio
async def test_opportunity_evaluation_structure(mock_shared_data):
    activity = MoneyEvaluationActivity()
    
    result = await activity.execute(mock_shared_data)
    
    evaluations = result.data["evaluations"]
    assert isinstance(evaluations, list)
    
    if evaluations:
        evaluation = evaluations[0]
        assert "opportunity" in evaluation
        assert "scores" in evaluation
        assert "overall_score" in evaluation
        assert "priority" in evaluation
        assert "recommendations" in evaluation
        
        scores = evaluation["scores"]
        assert "market_potential" in scores
        assert "feasibility" in scores
        assert "risk_level" in scores
        assert "profitability" in scores


@pytest.mark.asyncio
async def test_evaluation_scoring(mock_shared_data):
    activity = MoneyEvaluationActivity()
    
    result = await activity.execute(mock_shared_data)
    
    evaluations = result.data["evaluations"]
    if evaluations:
        evaluation = evaluations[0]
        assert 0 <= evaluation["overall_score"] <= 1
        assert evaluation["priority"] in ["High", "Medium", "Low"]
        
        for score in evaluation["scores"].values():
            assert 0 <= score <= 1


@pytest.mark.asyncio
async def test_recommendations_generation(mock_shared_data):
    activity = MoneyEvaluationActivity()
    
    result = await activity.execute(mock_shared_data)
    
    evaluations = result.data["evaluations"]
    if evaluations:
        evaluation = evaluations[0]
        recommendations = evaluation["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)


@pytest.mark.asyncio
async def test_data_freshness_check():
    activity = MoneyEvaluationActivity()
    
    # Test with fresh data
    assert activity._is_data_fresh(datetime.now().isoformat())
    
    # Test with old data
    old_timestamp = (datetime.now() - timedelta(hours=25)).isoformat()
    assert not activity._is_data_fresh(old_timestamp)
    
    # Test with invalid timestamp
    assert not activity._is_data_fresh("invalid-timestamp")


@pytest.mark.asyncio
async def test_market_potential_scoring():
    activity = MoneyEvaluationActivity()
    
    # Test high potential opportunity
    high_potential = {
        "sector": "technology",
        "insight": "Growing market with high demand"
    }
    high_score = activity._evaluate_market_potential(high_potential)
    assert high_score > 0.7
    
    # Test low potential opportunity
    low_potential = {
        "sector": "unknown",
        "insight": "Standard market conditions"
    }
    low_score = activity._evaluate_market_potential(low_potential)
    assert low_score < 0.7


@pytest.mark.asyncio
async def test_priority_level_assignment():
    activity = MoneyEvaluationActivity()
    
    assert activity._get_priority_level(0.9) == "High"
    assert activity._get_priority_level(0.7) == "Medium"
    assert activity._get_priority_level(0.4) == "Low"


@pytest.mark.asyncio
async def test_error_handling(mock_shared_data):
    activity = MoneyEvaluationActivity()
    
    # Remove required data to trigger error
    mock_shared_data.set("memory", "latest_market_research", None)
    
    result = await activity.execute(mock_shared_data)
    assert isinstance(result.data, dict)
    assert len(result.data.get("opportunities", [])) == 0