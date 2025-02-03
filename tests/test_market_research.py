"""Tests for the market research activity."""

import pytest
from datetime import datetime
from my_digital_being.activities.activity_market_research import MarketResearchActivity
from my_digital_being.framework.shared_data import SharedData


@pytest.fixture
def mock_shared_data():
    shared_data = SharedData()
    shared_data.initialize()
    return shared_data


@pytest.mark.asyncio
async def test_market_research_execution():
    activity = MarketResearchActivity()
    shared_data = SharedData()
    shared_data.initialize()
    
    result = await activity.execute(shared_data)
    
    assert result.success
    assert "market_data" in result.data
    assert "opportunities" in result.data
    assert "timestamp" in result.data
    assert isinstance(result.data["timestamp"], str)


@pytest.mark.asyncio
async def test_market_data_structure():
    activity = MarketResearchActivity()
    shared_data = SharedData()
    shared_data.initialize()
    
    result = await activity.execute(shared_data)
    
    market_data = result.data["market_data"]
    assert "news" in market_data
    assert "trends" in market_data
    assert "competitors" in market_data
    
    # Verify news structure
    if market_data["news"]:
        news_item = market_data["news"][0]
        assert "market" in news_item
        assert "title" in news_item
        assert "summary" in news_item
        assert "url" in news_item
        assert "timestamp" in news_item


@pytest.mark.asyncio
async def test_opportunities_analysis():
    activity = MarketResearchActivity()
    shared_data = SharedData()
    shared_data.initialize()
    
    result = await activity.execute(shared_data)
    
    opportunities = result.data["opportunities"]
    assert isinstance(opportunities, list)
    
    if opportunities:
        opportunity = opportunities[0]
        assert "market" in opportunity
        assert "type" in opportunity
        assert "title" in opportunity
        assert "insight" in opportunity
        assert "requirements" in opportunity
        assert isinstance(opportunity["requirements"], dict)


@pytest.mark.asyncio
async def test_market_research_storage():
    activity = MarketResearchActivity()
    shared_data = SharedData()
    shared_data.initialize()
    
    await activity.execute(shared_data)
    
    stored_research = shared_data.get("memory", "latest_market_research")
    assert stored_research is not None
    assert "market_data" in stored_research
    assert "opportunities" in stored_research
    assert "timestamp" in stored_research


@pytest.mark.asyncio
async def test_target_markets_coverage():
    activity = MarketResearchActivity()
    shared_data = SharedData()
    shared_data.initialize()
    
    result = await activity.execute(shared_data)
    
    assert "markets_analyzed" in result.metadata
    markets = result.metadata["markets_analyzed"]
    assert isinstance(markets, list)
    assert len(markets) > 0
    assert "saas" in markets  # Check for at least one expected market