"""Tests for Al Zait News Agent nodes."""

import pytest
import sys
import os

# Add src to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.agents.state import AgentState, create_initial_state
from src.nodes.fetch_news import fetch_news
from src.nodes.filter_articles import filter_articles
from src.nodes.cluster_events import cluster_events
from src.nodes.compile_brief import compile_brief


class TestAgentState:
    """Test the agent state management."""
    
    def test_create_initial_state(self):
        """Test initial state creation."""
        queries = ["test query 1", "test query 2"]
        state = create_initial_state(queries)
        
        assert state["search_queries"] == queries
        assert state["fetched_articles"] == []
        assert state["filtered_articles"] == []
        assert state["clustered_events"] == []
        assert state["final_brief"] == ""
        assert isinstance(state["errors"], list)


class TestFetchNewsNode:
    """Test the fetch_news node."""
    
    def test_fetch_news_empty_queries(self):
        """Test fetch_news with empty queries."""
        state = create_initial_state([])
        result_state = fetch_news(state)
        
        assert "fetched_articles" in result_state
        assert isinstance(result_state["fetched_articles"], list)
        assert "processing_stats" in result_state
    
    def test_fetch_news_with_queries(self):
        """Test fetch_news with valid queries."""
        state = create_initial_state(["test news"])
        result_state = fetch_news(state)
        
        assert "fetched_articles" in result_state
        assert isinstance(result_state["fetched_articles"], list)
        assert "articles_fetched" in result_state.get("processing_stats", {})


class TestFilterArticlesNode:
    """Test the filter_articles node."""
    
    def test_filter_articles_empty(self):
        """Test filter_articles with no articles."""
        state = create_initial_state(["test"])
        state["fetched_articles"] = []
        
        result_state = filter_articles(state)
        
        assert "filtered_articles" in result_state
        assert result_state["filtered_articles"] == []
        assert "processed_urls" in result_state
    
    def test_filter_articles_with_articles(self):
        """Test filter_articles with sample articles."""
        state = create_initial_state(["test"])
        state["fetched_articles"] = [
            {
                "title": "Test Article 1",
                "url": "https://test1.com",
                "content": "Test content 1",
                "source": "Test Source",
                "published_at": "2024-01-01",
                "language": "en"
            },
            {
                "title": "Test Article 2", 
                "url": "https://test2.com",
                "content": "Test content 2",
                "source": "Test Source",
                "published_at": "2024-01-01",
                "language": "ar"
            }
        ]
        
        result_state = filter_articles(state)
        
        assert "filtered_articles" in result_state
        assert isinstance(result_state["filtered_articles"], list)
        assert len(result_state["filtered_articles"]) <= len(state["fetched_articles"])


class TestClusterEventsNode:
    """Test the cluster_events node."""
    
    def test_cluster_events_empty(self):
        """Test cluster_events with no articles."""
        state = create_initial_state(["test"])
        state["filtered_articles"] = []
        
        result_state = cluster_events(state)
        
        assert "clustered_events" in result_state
        assert result_state["clustered_events"] == []
    
    def test_cluster_events_single_article(self):
        """Test cluster_events with single article."""
        state = create_initial_state(["test"])
        state["filtered_articles"] = [
            {
                "title": "Single Test Article",
                "url": "https://single-test.com",
                "content": "Single test content",
                "source": "Test Source",
                "published_at": "2024-01-01",
                "language": "en"
            }
        ]
        
        result_state = cluster_events(state)
        
        assert "clustered_events" in result_state
        assert result_state["clustered_events"] == [[0]]
    
    def test_cluster_events_multiple_articles(self):
        """Test cluster_events with multiple articles."""
        state = create_initial_state(["test"])
        state["filtered_articles"] = [
            {
                "title": "Article 1",
                "url": "https://test1.com", 
                "content": "Content about Sudan politics",
                "source": "Source 1",
                "published_at": "2024-01-01",
                "language": "en"
            },
            {
                "title": "Article 2",
                "url": "https://test2.com",
                "content": "Content about Sudan economy", 
                "source": "Source 2",
                "published_at": "2024-01-01",
                "language": "ar"
            }
        ]
        
        result_state = cluster_events(state)
        
        assert "clustered_events" in result_state
        assert isinstance(result_state["clustered_events"], list)
        assert len(result_state["clustered_events"]) > 0


class TestCompileBriefNode:
    """Test the compile_brief node."""
    
    def test_compile_brief_empty_summaries(self):
        """Test compile_brief with no summaries."""
        state = create_initial_state(["test"])
        state["event_summaries"] = []
        
        result_state = compile_brief(state)
        
        assert "final_brief" in result_state
        assert isinstance(result_state["final_brief"], str)
        assert len(result_state["final_brief"]) > 0
    
    def test_compile_brief_with_summaries(self):
        """Test compile_brief with sample summaries."""
        state = create_initial_state(["test"])
        state["event_summaries"] = [
            {
                "articles": [{"title": "Test 1", "source": "Source 1"}],
                "summary": "ملخص الخبر الأول عن السودان."
            },
            {
                "articles": [{"title": "Test 2", "source": "Source 2"}],
                "summary": "ملخص الخبر الثاني عن الاقتصاد السوداني."
            }
        ]
        
        result_state = compile_brief(state)
        
        assert "final_brief" in result_state
        assert isinstance(result_state["final_brief"], str)
        assert len(result_state["final_brief"]) > 0
        # Should contain Arabic text
        assert any('\u0600' <= c <= '\u06FF' for c in result_state["final_brief"])


class TestIntegration:
    """Integration tests for the workflow."""
    
    def test_state_flow(self):
        """Test that state flows correctly through multiple nodes."""
        # Start with initial state
        state = create_initial_state(["Sudan test"])
        
        # Simulate article fetching
        state["fetched_articles"] = [
            {
                "title": "Sudan News Article",
                "url": "https://example.com/sudan-news",
                "content": "Important news about Sudan politics and economy.",
                "source": "Test News",
                "published_at": "2024-01-01T10:00:00Z",
                "language": "en"
            }
        ]
        
        # Run through filter node
        state = filter_articles(state)
        assert "filtered_articles" in state
        
        # Run through cluster node  
        state = cluster_events(state)
        assert "clustered_events" in state
        
        # Check state consistency
        assert isinstance(state["errors"], list)
        assert "processing_stats" in state
        
        # Verify that each node adds its expected data
        expected_keys = [
            "search_queries", "fetched_articles", "filtered_articles", 
            "clustered_events", "processing_stats", "errors"
        ]
        
        for key in expected_keys:
            assert key in state, f"Missing key: {key}"


if __name__ == "__main__":
    pytest.main([__file__])
