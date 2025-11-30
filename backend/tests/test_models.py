"""Tests for Pydantic models."""
import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from adk_agent import DiscoveredLead, DiscoveredLeadsReport, GrantData


def test_discovered_lead_creation():
    """Test creating a DiscoveredLead."""
    lead = DiscoveredLead(
        url="https://example.com/grant",
        source="Example Foundation",
        title="Community Grant"
    )
    assert lead.url == "https://example.com/grant"
    assert lead.source == "Example Foundation"
    assert lead.title == "Community Grant"


def test_discovered_lead_defaults():
    """Test DiscoveredLead default values."""
    lead = DiscoveredLead(
        url="https://example.com/grant",
        source="Test Foundation"
    )
    assert lead.title == ""


def test_discovered_leads_report():
    """Test DiscoveredLeadsReport with multiple leads."""
    leads = [
        DiscoveredLead(url="https://example1.com", source="Foundation 1", title="Grant 1"),
        DiscoveredLead(url="https://example2.com", source="Foundation 2", title="Grant 2")
    ]
    report = DiscoveredLeadsReport(discovered_leads=leads)
    
    assert len(report.discovered_leads) == 2
    assert report.discovered_leads[0].title == "Grant 1"
    assert report.discovered_leads[1].title == "Grant 2"


def test_grant_data_defaults():
    """Test GrantData with default values."""
    grant = GrantData(url="https://example.com/grant")
    
    assert grant.title == "Untitled Grant"
    assert grant.funder == "Unknown"
    assert grant.deadline == "Not specified"
    assert grant.amount == "Not specified"
    assert grant.description == "No description available"
    assert grant.detailed_overview == "No detailed overview available"
    assert grant.tags == []
    assert grant.eligibility == "Not specified"
    assert grant.url == "https://example.com/grant"
    assert grant.application_requirements == []
    assert grant.funding_type == "Grant"
    assert grant.geography == "Not specified"


def test_grant_data_full():
    """Test GrantData with all fields populated."""
    grant = GrantData(
        title="Community Garden Grant",
        funder="Green Foundation",
        deadline="2025-12-31",
        amount="$10,000 - $25,000",
        description="Funding for community gardens",
        detailed_overview="This grant supports urban gardening initiatives...",
        tags=["Community", "Gardens", "Urban"],
        eligibility="501(c)(3) organizations",
        url="https://example.com/grant",
        application_requirements=["Tax ID", "Budget", "Project Plan"],
        funding_type="Grant",
        geography="Chicago, IL"
    )
    
    assert grant.title == "Community Garden Grant"
    assert grant.funder == "Green Foundation"
    assert grant.deadline == "2025-12-31"
    assert grant.amount == "$10,000 - $25,000"
    assert len(grant.tags) == 3
    assert len(grant.application_requirements) == 3
    assert grant.geography == "Chicago, IL"


def test_grant_data_to_dict():
    """Test converting GrantData to dictionary."""
    grant = GrantData(
        title="Test Grant",
        funder="Test Foundation",
        url="https://example.com"
    )
    
    grant_dict = grant.model_dump()
    
    assert isinstance(grant_dict, dict)
    assert grant_dict["title"] == "Test Grant"
    assert grant_dict["funder"] == "Test Foundation"
    assert grant_dict["url"] == "https://example.com"
    assert "deadline" in grant_dict
    assert "amount" in grant_dict


def test_discovered_lead_validation():
    """Test DiscoveredLead field validation."""
    with pytest.raises(Exception):  # Pydantic will raise validation error
        DiscoveredLead(source="Test")  # Missing required 'url' field
