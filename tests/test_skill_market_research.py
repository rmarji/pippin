"""Tests for the market research skill."""

import pytest
from datetime import datetime
from my_digital_being.skills.skill_market_research import MarketResearchSkill


@pytest.fixture
def market_skill():
    return MarketResearchSkill(api_key="test_api_key")


@pytest.mark.asyncio
async def test_search_market_news(market_skill):
    query = "saas market trends"
    results = await market_skill.search_market_news(query)
    
    assert isinstance(results, list)
    if results:  # If Linkup API returns results
        news_item = results[0]
        assert "title" in news_item
        assert "summary" in news_item
        assert "url" in news_item
        assert "source" in news_item
        assert "timestamp" in news_item
        assert isinstance(news_item["timestamp"], str)


@pytest.mark.asyncio
async def test_analyze_market_trends(market_skill):
    market = "saas"
    focus_areas = ["emerging trends", "market size"]
    
    result = await market_skill.analyze_market_trends(market, focus_areas)
    
    assert isinstance(result, dict)
    assert "market" in result
    assert result["market"] == market
    assert "trends" in result
    assert "timestamp" in result
    
    if result["trends"]:  # If trends were found
        trend = result["trends"][0]
        assert "focus_area" in trend
        assert "insights" in trend
        if trend["insights"]:
            insight = trend["insights"][0]
            assert "title" in insight
            assert "summary" in insight
            assert "source" in insight


@pytest.mark.asyncio
async def test_research_competitors(market_skill):
    market = "saas"
    competitor_types = ["established", "startup"]
    
    result = await market_skill.research_competitors(market, competitor_types)
    
    assert isinstance(result, dict)
    assert "market" in result
    assert result["market"] == market
    assert "segments" in result
    assert "timestamp" in result
    
    if result["segments"]:  # If competitors were found
        segment = result["segments"][0]
        assert "segment" in segment
        assert "competitors" in segment
        if segment["competitors"]:
            competitor = segment["competitors"][0]
            assert "name" in competitor
            assert "description" in competitor
            assert "source" in competitor


@pytest.mark.asyncio
async def test_max_results_limit(market_skill):
    query = "technology trends"
    max_results = 3
    
    results = await market_skill.search_market_news(query, max_results=max_results)
    
    assert len(results) <= max_results


@pytest.mark.asyncio
async def test_error_handling(market_skill):
    # Test with invalid API key
    market_skill = MarketResearchSkill(api_key="invalid_key")
    results = await market_skill.search_market_news("test query")
    
    assert isinstance(results, list)
    assert len(results) == 0  # Should return empty list on error


@pytest.mark.asyncio
async def test_timestamp_format(market_skill):
    query = "test market"
    results = await market_skill.search_market_news(query)
    
    if results:
        timestamp = results[0]["timestamp"]
        # Verify ISO format
        try:
            datetime.fromisoformat(timestamp)
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp}")


@pytest.mark.asyncio
async def test_empty_query_handling(market_skill):
    results = await market_skill.search_market_news("")
    assert isinstance(results, list)
    assert len(results) == 0  # Should handle empty query gracefully