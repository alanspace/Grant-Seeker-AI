"""Unit tests for models."""
import pytest
from backend.models import DiscoveredLead, DiscoveredLeadsReport, GrantData


def test_discovered_lead_creation():
    """Test creating a DiscoveredLead."""
    lead = DiscoveredLead(
        url="https://example.com/grant",
        source="Example Foundation",
        title="Test Grant"
    )
    
    assert lead.url == "https://example.com/grant"
    assert lead.source == "Example Foundation"
    assert lead.title == "Test Grant"


def test_discovered_lead_defaults():
    """Test DiscoveredLead default values."""
    lead = DiscoveredLead(
        url="https://example.com/grant",
        source="Example Foundation"
    )
    
    assert lead.title == ""


def test_grant_data_defaults():
    """Test GrantData default values."""
    grant = GrantData()
    
    assert grant.id == 0
    assert grant.title == "Untitled Grant"
    assert grant.funder == "Unknown"
    assert grant.deadline == "Not specified"
    assert grant.amount == "Not specified"
    assert grant.tags == []
    assert grant.application_requirements == []


def test_grant_data_full():
    """Test GrantData with all fields."""
    grant = GrantData(
        id=1,
        title="Community Grant",
        funder="Foundation X",
        deadline="2025-12-31",
        amount="$10,000",
        description="Test description",
        detailed_overview="Test overview",
        tags=["Community", "Education"],
        eligibility="Test eligibility",
        url="https://example.com/grant",
        application_requirements=["501(c)(3)", "Budget"],
        funding_type="Grant",
        geography="Chicago"
    )
    
    assert grant.id == 1
    assert grant.title == "Community Grant"
    assert len(grant.tags) == 2
    assert len(grant.application_requirements) == 2


def test_discovered_leads_report():
    """Test DiscoveredLeadsReport."""
    leads = [
        DiscoveredLead(url="https://example1.com", source="Org1", title="Grant1"),
        DiscoveredLead(url="https://example2.com", source="Org2", title="Grant2")
    ]
    
    report = DiscoveredLeadsReport(discovered_leads=leads)
    
    assert len(report.discovered_leads) == 2
    assert report.discovered_leads[0].title == "Grant1"
