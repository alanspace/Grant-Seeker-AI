"""LLM agents for Grant Seeker application."""
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import types

from config import Config
from utils.helpers import get_current_date


def create_retry_config() -> types.HttpRetryOptions:
    """Create retry configuration for Gemini API.
    
    Returns:
        HttpRetryOptions instance
    """
    return types.HttpRetryOptions(
        attempts=Config.RETRY_ATTEMPTS,
        exp_base=Config.RETRY_EXP_BASE,
        initial_delay=Config.RETRY_INITIAL_DELAY,
        http_status_codes=Config.RETRY_STATUS_CODES,
    )


def create_finder_agent() -> LlmAgent:
    """Create the grant finder agent.
    
    Returns:
        LlmAgent configured for finding grants
    """
    return LlmAgent(
        name="GrantFinder",
        model=Gemini(model=Config.MODEL_NAME, retry_options=create_retry_config()),
        instruction="""
        You are a Grant Scout. You will receive search results from Tavily.
        Your job is to analyze these results and identify the top 5-7 most promising grant opportunities.
        
        Return a JSON object with a 'discovered_leads' list.
        Each lead must have:
        - 'url': the URL of the grant page
        - 'source': the name of the organization
        - 'title': the grant title or program name
        
        Focus on official funder pages and active grant programs, NOT grant directories or lists.
        
        Example format:
        {
          "discovered_leads": [
            {"url": "https://example.com/grant", "source": "Example Foundation", "title": "Community Grant"}
          ]
        }
        """
    )


def create_extractor_agent() -> LlmAgent:
    """Create the grant extractor agent.
    
    Returns:
        LlmAgent configured for extracting grant data
    """
    current_date, current_date_iso = get_current_date()
    
    return LlmAgent(
        name="GrantExtractor",
        model=Gemini(model=Config.MODEL_NAME, retry_options=create_retry_config()),
        instruction=f"""
        You are a Data Extractor. You will receive the content of a grant webpage.

        IMPORTANT - CURRENT DATE CONTEXT:
        Today's date is: {current_date} ({current_date_iso})
        Only extract grants with deadlines in the FUTURE (after {current_date_iso}).
        If a deadline has already passed, note it but mark as expired.
        
        Extract the following information and return as a JSON object:
        
        Required fields:
        - title: The grant program name/title
        - funder: The organization or foundation offering the grant
        - deadline: Application deadline date (BE THOROUGH - look for ANY dates, cycles, rounds)
        - amount: Funding amount (BE THOROUGH - look for $, ranges, "up to", award amounts)
        - description: Brief 1-2 sentence summary of what the grant funds
        - detailed_overview: Comprehensive description of the grant program, goals, and purpose
        - tags: Array of relevant category tags (e.g., ["Education", "Youth", "Community"])
        - eligibility: Full eligibility requirements text
        - url: The URL provided
        - application_requirements: Array of application requirements (e.g., ["501(c)(3) status", "Program budget"])
        - funding_type: Type of funding (default to "Grant")
        - geography: Geographic scope or location requirements (e.g., "Chicago", "Illinois", "United States")
        
        CRITICAL - Deadline & Amount Extraction:
        - deadline: Search ENTIRE page for dates! Look for "deadline", "due", "apply by", "submit by", grant cycles, fiscal years
          * If you find "rolling" or "ongoing", use "Rolling deadline"
          * If multiple cycles, list the NEXT upcoming date AFTER {current_date_iso}
          * Format as YYYY-MM-DD if possible
          * If deadline is BEFORE {current_date_iso}, use "Expired (YYYY-MM-DD)"
        - amount: Search ENTIRE page for dollar signs, numbers, ranges!
          * Look in titles, headings, tables, fine print
          * If you see "up to $X", use exactly "Up to $X"
          * If range "$5,000-$25,000", format as "$5,000 - $25,000"
        
        Other requirements:
        - Extract actual data from the page content
        - If truly not found after thorough search, use defaults
        - Be thorough with detailed_overview
        - Generate 3-5 relevant tags based on content
        
        Example format:
        {{
          "title": "Community Garden Grant Program",
          "funder": "Green Cities Foundation",
          "deadline": "2026-05-15",
          "amount": "$1,000 - $5,000",
          "description": "Funding for urban community gardens that serve youth populations.",
          "detailed_overview": "The Community Garden Grant Program supports urban gardens...",
          "tags": ["Community", "Gardens", "Youth", "Urban"],
          "eligibility": "501(c)(3) non-profit organizations serving Chicago communities",
          "url": "https://example.com/grant",
          "application_requirements": ["501(c)(3) status", "Project budget", "Site plan"],
          "funding_type": "Grant",
          "geography": "Chicago, Illinois"
        }}
        """
    )
