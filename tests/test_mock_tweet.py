"""Tests for the mock tweet activity."""

import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_digital_being.activities.activity_mock_tweet import MockTweetActivity
from my_digital_being.framework.shared_data import SharedData
from datetime import datetime


@pytest.fixture
def mock_shared_data():
    shared_data = SharedData()
    shared_data.initialize()  # Initialize the data structure
    # Add some test news data
    shared_data.set("memory", "latest_news", [
        {
            "title": "Test News Article",
            "topic": "technology",
            "summary": "This is a test article",
            "url": "https://example.com/test"
        }
    ])
    return shared_data


@pytest.mark.asyncio
async def test_mock_tweet_creation():
    activity = MockTweetActivity()
    shared_data = SharedData()
    shared_data.initialize()  # Initialize the data structure
    
    result = await activity.execute(shared_data)
    
    assert result.success
    assert isinstance(result.data.get("content"), str)
    assert len(result.data.get("content")) <= 280
    assert result.metadata.get("length") <= 280


@pytest.mark.asyncio
async def test_mock_tweet_with_news(mock_shared_data):
    activity = MockTweetActivity()
    
    result = await activity.execute(mock_shared_data)
    
    assert result.success
    assert "Test News Article" in result.data.get("content")
    assert "#News" in result.data.get("content")


@pytest.mark.asyncio
async def test_mock_tweet_storage(mock_shared_data):
    activity = MockTweetActivity()
    
    await activity.execute(mock_shared_data)
    
    stored_tweet = mock_shared_data.get("memory", "latest_mock_tweet")
    assert stored_tweet is not None
    assert isinstance(stored_tweet.get("content"), str)
    assert isinstance(stored_tweet.get("timestamp"), (str, datetime))


@pytest.mark.asyncio
async def test_mock_tweet_length_limit():
    activity = MockTweetActivity()
    shared_data = SharedData()
    
    # Set up very long news title
    shared_data.initialize()  # Initialize the data structure
    shared_data.set("memory", "latest_news", [{
        "title": "x" * 300,
        "topic": "test",
        "summary": "Long test article",
        "url": "https://example.com/long"
    }])
    
    result = await activity.execute(shared_data)
    
    assert result.success
    assert len(result.data.get("content")) <= 280
    assert result.data.get("content").endswith("...")