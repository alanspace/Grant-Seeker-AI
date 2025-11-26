"""Pytest configuration and fixtures."""
import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_tavily_client():
    """Create a mock Tavily client."""
    client = MagicMock()
    client.search = AsyncMock(return_value=[
        {
            "title": "Test Grant 1",
            "url": "https://example.com/grant1",
            "content": "Test content for grant 1"
        },
        {
            "title": "Test Grant 2",
            "url": "https://example.com/grant2",
            "content": "Test content for grant 2"
        }
    ])
    client.get_page_content = AsyncMock(return_value="Mock grant page content with deadline and amount")
    return client


@pytest.fixture
def mock_session_service():
    """Create a mock session service."""
    service = MagicMock()
    service.create_session = AsyncMock()
    return service


@pytest.fixture
def sample_discovered_lead():
    """Create a sample DiscoveredLead."""
    from models import DiscoveredLead
    return DiscoveredLead(
        url="https://example.com/grant",
        source="Example Foundation",
        title="Community Grant"
    )


@pytest.fixture
def sample_grant_data():
    """Create sample grant data."""
    return {
        "id": 1,
        "title": "Community Garden Grant",
        "funder": "Green Foundation",
        "deadline": "2025-12-31",
        "amount": "$5,000 - $10,000",
        "description": "Funding for community gardens",
        "detailed_overview": "This grant supports urban community gardens...",
        "tags": ["Community", "Gardens", "Urban"],
        "eligibility": "501(c)(3) organizations",
        "url": "https://example.com/grant",
        "application_requirements": ["501(c)(3) status", "Budget"],
        "funding_type": "Grant",
        "geography": "Chicago, Illinois"
    }
