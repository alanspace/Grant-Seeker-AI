"""Pydantic models for Grant Seeker application."""
from pydantic import BaseModel


class DiscoveredLead(BaseModel):
    """A discovered grant lead from search results."""
    url: str
    source: str
    title: str = ""


class DiscoveredLeadsReport(BaseModel):
    """Report containing discovered grant leads."""
    discovered_leads: list[DiscoveredLead]


class GrantData(BaseModel):
    """Complete grant data structure."""
    id: int = 0
    title: str = "Untitled Grant"
    funder: str = "Unknown"
    deadline: str = "Not specified"
    amount: str = "Not specified"
    description: str = "No description available"
    detailed_overview: str = "No detailed overview available"
    tags: list[str] = []
    eligibility: str = "Not specified"
    url: str = ""
    application_requirements: list[str] = []
    funding_type: str = "Grant"
    geography: str = "Not specified"
