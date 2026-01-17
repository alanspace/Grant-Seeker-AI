"""
Grant Seeker Agent - Single file version with caching
Consolidated from refactored architecture while maintaining caching functionality

This module serves as the main backend orchestrator for the Grant Seeker application.
It handles:
1.  **Workflow Orchestration**: Managing the multi-step process of finding and extracting grants.
2.  **Agent Definitions**: Defining the specific AI agents (Finder, Extractor, QueryGenerator).
3.  **Caching**: Storing search results and extracted data to improve performance and reduce API costs.
4.  **Data Models**: Defining the structure of the data using Pydantic models.
"""
import os
import re
import time
import asyncio
import json
import hashlib
import logging
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import httpx # For URL validation
from typing import Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel
try:
    from backend.tavily_client import TavilyClient
    from backend.content_extractor import RobustContentExtractor, is_viable_grant
except ImportError:
    from tavily_client import TavilyClient
    from content_extractor import RobustContentExtractor, is_viable_grant

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Set root logger to WARNING
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Set our app logger to INFO
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()
load_dotenv("../.env")

# ============================================================================
# CONFIGURATION
# ============================================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Validate required API keys
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY must be set in .env file")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY (for Gemini) must be set in .env file")

MODEL_NAME = "gemini-flash-latest"
TAVILY_MAX_RESULTS = 10
MAX_CONCURRENT_EXTRACTIONS = 3
CONTENT_PREVIEW_LENGTH = 3000

# Cache settings
CACHE_ENABLED = True
CACHE_DIR = ".cache"
CACHE_TTL_HOURS = 24

# Retry configuration
RETRY_ATTEMPTS = 1
RETRY_EXP_BASE = 2
RETRY_INITIAL_DELAY = 1.0
RETRY_STATUS_CODES = [429, 500, 503, 504]

# ============================================================================
# UTILITY FUNCTIONS
# Helper functions for date handling, string normalization, and cleaning.
# ============================================================================

def get_current_date() -> tuple[str, str]:
    """Get current date in human-readable and ISO format."""
    now = datetime.now()
    return (
        now.strftime("%B %d, %Y"),
        now.strftime("%Y-%m-%d")
    )

def normalize_value(value: str | None, default: str) -> str:
    """Convert empty strings, None, or whitespace-only strings to default value."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return default
    return value


# ============================================================================
# CACHE SERVICE
# A simple file-based caching system to store API responses.
# This prevents redundant API calls for the same queries or URLs, saving time and money.
# ============================================================================

class CacheService:
    """Simple file-based cache for search results and page content."""
    
    def __init__(self, cache_dir: str = ".cache", ttl_hours: int = 24):
        """Initialize cache service."""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        logger.info(f"Cache initialized at {self.cache_dir} with TTL={ttl_hours}h")
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache filename from key."""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get full path for cache file."""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, key: str) -> Optional[dict]:
        """Retrieve data from cache if not expired."""
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            logger.debug(f"Cache miss: {key}")
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check expiration
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cached_at > self.ttl:
                logger.debug(f"Cache expired: {key}")
                cache_path.unlink()
                return None
            
            logger.info(f"Cache hit: {key}")
            return cache_data['data']
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Invalid cache file: {cache_path}, error: {e}")
            cache_path.unlink()
            return None
    
    def set(self, key: str, data: dict) -> None:
        """Store data in cache."""
        cache_key = self._get_cache_key(key)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'key': key,
            'data': data
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cached: {key}")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Failed to cache {key}: {error_type}: {str(e)[:100]}")
    
    def clear(self) -> int:
        """Clear all cache files."""
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1
        logger.info(f"Cleared {count} cache files")
        return count

# ============================================================================
# PYDANTIC MODELS
# These models define the strict schema for data validation.
# They ensure that the AI agents return structured data that the UI can reliably display.
# ============================================================================

class DiscoveredLead(BaseModel):
    """A discovered grant lead from search results."""
    url: str
    source: str
    title: str = ""

class DiscoveredLeadsReport(BaseModel):
    """Report containing discovered grant leads."""
    discovered_leads: list[DiscoveredLead]

class GrantData(BaseModel):
    """Detailed grant data."""
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
    funding_nature: str = "Unknown"
    geography: str = "Not specified"
    fit_score: int = 0
    founder_demographics: list[str] = []

def normalize_funding_nature(value: str | None) -> str:
    """Normalize funding type to 'Grant', 'Loan', 'Tax Credit' or 'Unknown'."""
    if not value:
        return "Unknown"
    
    val_lower = value.lower()
    if "tax credit" in val_lower:
        return "Tax Credit"
    if "loan" in val_lower:
        return "Loan"
    if "grant" in val_lower:
        return "Grant"
        
    return "Unknown"

def calculate_fit_score(grant_data: dict, query: str) -> int:
    """Calculate a fit score (0-100) based on query match."""
    if not query:
        return 0
        
    query_terms = set(query.lower().split())
    # Remove common stop words
    stop_words = {'a', 'an', 'the', 'and', 'or', 'for', 'of', 'in', 'to', 'with', 'on', 'at', 'by'}
    keywords = query_terms - stop_words
    
    if not keywords:
        return 0
        
    score = 0
    max_score = len(keywords) * 10  # Arbitrary max score basis
    
    # Weights
    TITLE_WEIGHT = 3
    TAGS_WEIGHT = 2
    DESC_WEIGHT = 1
    
    text_title = grant_data.get('title', '').lower()
    text_desc = (grant_data.get('description', '') + ' ' + grant_data.get('detailed_overview', '')).lower()
    tags = [t.lower() for t in grant_data.get('tags', [])]
    
    matches = 0
    for word in keywords:
        word_matched = False
        
        # Check title
        if word in text_title:
            score += TITLE_WEIGHT
            word_matched = True
            
        # Check tags
        if any(word in t for t in tags):
            score += TAGS_WEIGHT
            word_matched = True
            
        # Check description
        if word in text_desc:
            score += DESC_WEIGHT
            word_matched = True
            
        if word_matched:
            matches += 1
            
    # Normalize to 0-100
    # Base the percentage mainly on how many keywords were found at least once
    coverage_score = (matches / len(keywords)) * 100
    
    # Add bonus for high relevance (multiple hits) but cap at 100
    final_score = min(100, int(coverage_score + (score * 2)))
    
    return final_score

# ============================================================================
# AGENT CREATION
# This section defines the specific AI agents using the Google ADK.
# Each agent has a specific "persona" and set of instructions (prompt engineering).
# ============================================================================

def create_retry_config() -> types.HttpRetryOptions:
    """Create retry configuration for Gemini API."""
    return types.HttpRetryOptions(
        attempts=RETRY_ATTEMPTS,
        exp_base=RETRY_EXP_BASE,
        initial_delay=RETRY_INITIAL_DELAY,
        http_status_codes=RETRY_STATUS_CODES,
    )

def create_finder_agent() -> LlmAgent:
    """Create the grant finder agent with structured output schema."""
    return LlmAgent(
        name="GrantFinder",
        model=Gemini(
            model=MODEL_NAME,
            retry_options=create_retry_config(),
            generation_config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DiscoveredLeadsReport
            )
        ),
        # The GrantFinder agent is responsible for filtering search results.
        # It looks at the raw list of URLs from Tavily and decides which ones are worth investigating further.
        # Output schema ensures structured JSON matching DiscoveredLeadsReport model.
        instruction="""
        You are a Grant Scout specializing in CANADIAN grants, loans, and tax credits.
        You will receive search results from Tavily.
        Your job is to analyze these results and identify the top 5-7 most promising CANADIAN grant opportunities.
        
        CRITICAL FILTERING RULES:
        - ONLY select grants from Canadian sources (Government of Canada, provincial governments, Canadian foundations)
        - EXCLUDE any USA grants (federal, state, or US-based foundations)
        - Look for .gc.ca, .canada.ca, provincial .ca domains, and Canadian organization websites
        - Verify the source is Canadian before including it
        
        Return a structured response with discovered_leads list.
        Each lead must have:
        - url: the URL of the grant page
        - source: the name of the Canadian organization
        - title: the grant title or program name
        
        Focus on official Canadian funder pages and active grant programs, NOT grant directories or lists.
        
        IMPORTANT: Return RAW JSON only. Do not include markdown formatting like ```json ... ```. 
        Start with { and end with }.
        """
    )

def create_extractor_agent() -> LlmAgent:
    """Create the grant extractor agent with structured output schema."""
    current_date, current_date_iso = get_current_date()
    
    return LlmAgent(
        name="GrantExtractor",
        model=Gemini(
            model=MODEL_NAME,
            retry_options=create_retry_config(),
            generation_config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GrantData
            )
        ),
        # The GrantExtractor agent is the heavy lifter.
        # It reads the full text of a webpage and extracts structured data (deadlines, amounts, eligibility).
        # We inject the current date so it can intelligently determine if a grant is expired.
        # Output schema ensures structured JSON matching GrantData model.
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
        - funding_nature: Type of funding (Must be "Grant", "Loan", "Tax Credit", or "Unknown")
        - geography: Geographic scope. ONLY extract CANADIAN grants, loans, and tax credits:
          * "Federal - Canada" -> if keywords: "Government of Canada", "Federal", "Canada-wide", "National", "Canadian"
          * "[Province Name]" -> if specific to a province (e.g., "Ontario", "British Columbia", "Quebec")
          * "[City, Province]" -> if city-specific (e.g., "Toronto, Ontario", "Vancouver, BC")
          * If you detect USA geography (states, US federal, American cities), SKIP this grant entirely or mark as "USA - Not Applicable"
        - founder_demographics: Tag any specific demographics focus. List of strings. PRIORITIZE these keywords:
          * "Women" -> if keywords: "Women", "Female", "Girl", "She/Her", "Women-owned"
          * "Youth" -> if keywords: "Youth", "Student", "Young Entrepreneur", "Next Gen" or ages 15-30
          * "Indigenous" -> if keywords: "Indigenous", "First Nations", "Inuit", "Métis", "Aboriginal Peoples", "Inuk"
          Also tag other demographic groups if mentioned (e.g., "Veterans", "LGBTQ+", "Immigrants", "People with Disabilities", "Minorities", etc.)
        
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
          "funding_nature": "Grant",
          "geography": "Federal - Canada",
          "founder_demographics": ["Women", "Youth", "Indigenous"]
        }}
        """
    )

def create_query_agent() -> LlmAgent:
    """Create the query generation agent."""
    return LlmAgent(
        name="QueryGenerator",
        model=Gemini(model=MODEL_NAME, retry_options=create_retry_config()),
        # The QueryGenerator agent translates a user's natural language project description
        # into a keyword-optimized search query for the search engine.
        instruction="""
        You are a Search Query Expert. Your job is to convert a user's project description into a targeted search query for finding grants IN CANADA ONLY.
        
        Rules:
        1. Extract the core topic (e.g., "community garden", "youth education", "renewable energy").
        2. Identify the location if mentioned, but ALWAYS prioritize Canadian context.
        3. Identify the target audience (e.g., "non-profit", "schools").
        4. Combine these into a concise search query string.
        5. ALWAYS add "Canada" or "Canadian" to the query to ensure Canadian results.
        6. Add keywords like "grants", "funding", "application", "deadline".
        7. Exclude USA-specific terms unless explicitly converting them to Canadian equivalents.
        8. Return ONLY the query string, no other text.
        
        Example Input: "We are a non-profit looking to build a community garden."
        Example Output: community garden grants Canada non-profit funding application
        
        Example Input: "Youth education program in Toronto"
        Example Output: youth education grants Toronto Ontario Canada funding
        """
    )

# ============================================================================
# MAIN WORKFLOW
# The GrantSeekerWorkflow class ties everything together.
# It manages the state, initializes agents, and executes the 4-phase process.
# ============================================================================

class GrantSeekerWorkflow:
    """Main workflow orchestrator for grant seeking with integrated caching."""
    
    def __init__(self):
        """Initialize the grant seeker workflow."""
        # Initialize cache service
        self.cache = None
        if CACHE_ENABLED:
            self.cache = CacheService(cache_dir=CACHE_DIR, ttl_hours=CACHE_TTL_HOURS)
        
        # Initialize Tavily client
        self.tavily = TavilyClient(api_key=TAVILY_API_KEY, max_retries=2, timeout=15.0)
        
        # Initialize robust content extractor with fallback strategies
        self.content_extractor = RobustContentExtractor(
            tavily_client=self.tavily,
            google_client=None,  # Will be set if Google is configured
            timeout=30.0
        )
        
        # Initialize session service
        self.session_service = InMemorySessionService()
        
        # Create agents
        self.finder_agent = create_finder_agent()
        self.extractor_agent = create_extractor_agent()
        self.query_agent = create_query_agent()

    def _is_grant_expired(self, grant_data: dict) -> bool:
        """Check if a grant is expired based on its deadline."""
        deadline = grant_data.get('deadline', '')
        if not deadline:
            return False
            
        deadline_lower = deadline.lower()
        
        # Check for explicit "expired" label from LLM
        if "expired" in deadline_lower:
            return True
            
        # Try to parse date in multiple formats
        try:
            # Try YYYY-MM-DD pattern first
            match = re.search(r'(\d{4}-\d{2}-\d{2})', deadline)
            if match:
                date_str = match.group(1)
                grant_date = datetime.strptime(date_str, "%Y-%m-%d")
                # Compare with today
                if grant_date.date() < datetime.now().date():
                    return True
            
            # Try DD-MM-YYYY pattern
            match = re.search(r'(\d{2}-\d{2}-\d{4})', deadline)
            if match:
                date_str = match.group(1)
                grant_date = datetime.strptime(date_str, "%d-%m-%Y")
                # Compare with today
                if grant_date.date() < datetime.now().date():
                    return True
        except Exception:
            pass # Parsing failed, assume not expired
            
        return False
    
    def _is_usa_grant(self, grant_data: dict) -> bool:
        """Check if a grant is from the USA and should be filtered out."""
        geography = grant_data.get('geography', '').lower()
        
        # Check for explicit USA markers
        if 'usa' in geography or 'united states' in geography or 'not applicable' in geography:
            return True
        
        # Check for US state names (common ones)
        us_states = [
            'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado',
            'connecticut', 'delaware', 'florida', 'georgia', 'hawaii', 'idaho',
            'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana',
            'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota',
            'mississippi', 'missouri', 'montana', 'nebraska', 'nevada',
            'new hampshire', 'new jersey', 'new mexico', 'new york',
            'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon',
            'pennsylvania', 'rhode island', 'south carolina', 'south dakota',
            'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington',
            'west virginia', 'wisconsin', 'wyoming'
        ]
        
        for state in us_states:
            if state in geography:
                return True
        
        return False



    async def generate_search_query(self, description: str) -> str:
        try:
            logger.info("Generating search query from description")
            
            # --- THE FIX: Create a UNIQUE session every time ---
            session_id = f"query-gen-{uuid.uuid4()}"
            
            # Create the session explicitly
            await self.session_service.create_session(
                app_name="grant-seeker",
                user_id="user-1",
                session_id=session_id
            )

            runner = Runner(
                agent=self.query_agent,
                app_name="grant-seeker",
                session_service=self.session_service
            )
                
            user_msg = types.Content(role="user", parts=[types.Part(text=description)])
            
            response_text = ""
            async for event in runner.run_async(
                user_id="user-1",
                session_id=session_id,
                new_message=user_msg
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    response_text = event.content.parts[0].text
            
            query = response_text.strip()
            logger.info(f"Generated query: {query}")
            return query
                
        except Exception as e:
            logger.error(f"Failed to generate query: {e}")
            # Fallback: use the first 10 words of the description
            return " ".join(description.split()[:10]) + " grants"
    
    async def search_grants(self, query: str) -> list[dict]:
        """Search for grants using Tavily API with caching."""
        # Check cache first
        cache_key = f"search:{query}:{TAVILY_MAX_RESULTS}"
        if self.cache:
            cached_results = self.cache.get(cache_key)
            if cached_results is not None:
                logger.info(f"Using cached search results for: {query}")
                return cached_results
        
        # Perform search
        try:
            logger.info(f"Searching for grants with query: {query}")
            results = await self.tavily.search(query, max_results=TAVILY_MAX_RESULTS)
            logger.info(f"Found {len(results)} search results")
            
            # Cache results
            if self.cache:
                self.cache.set(cache_key, results)
            
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    async def analyze_results(self, search_results: list[dict], session_id: str) -> list[DiscoveredLead]:
        """Analyze search results to identify promising grants."""
        try:
            logger.info("Analyzing search results with LLM")
            
            # Format results for the agent
            formatted_results = json.dumps(search_results, indent=2)
            prompt = f"Analyze these Tavily search results and identify the top 5-7 most promising grant opportunities:\n\n{formatted_results}"
            
            # Run agent
            runner = Runner(
                agent=self.finder_agent,
                app_name="grant-seeker",
                session_service=self.session_service
            )
            
            user_msg = types.Content(role="user", parts=[types.Part(text=prompt)])
            
            response_text = ""
            async for event in runner.run_async(
                user_id="user-1",
                session_id=session_id,
                new_message=user_msg
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    response_text = event.content.parts[0].text
            
            
            if not response_text:
                logger.error("No response text received from agent")
                return []
            
            # Clean up response text (remove markdown if present)
            response_text = response_text.replace("```json", "").replace("```", "").strip()

            # Parse response using Pydantic (output schema guarantees valid JSON)
            try:
                leads_data = DiscoveredLeadsReport.model_validate_json(response_text)
                logger.info(f"Identified {len(leads_data.discovered_leads)} promising grants")
                return leads_data.discovered_leads
            except Exception as e:
                logger.error(f"Failed to parse leads: {e}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to analyze results: {e}")
            return []
    
    async def extract_grant_data(self, lead: DiscoveredLead, query: str = "") -> dict:
        """Extract detailed grant data from a URL with caching."""
        # Check cache first
        cache_key = f"extract:{lead.url}"
        if self.cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"Using cached extraction for: {lead.url}")
                # Recalculate fit score if query is provided, as it might be different
                if query:
                    cached_data['fit_score'] = calculate_fit_score(cached_data, query)
                return cached_data
        
        # Create session for this extraction
        session_id = f"extract-{hashlib.md5(lead.url.encode()).hexdigest()[:8]}-{uuid.uuid4()}"
        await self.session_service.create_session(
            app_name="grant-seeker",
            user_id="user-1",
            session_id=session_id
        )
        
        try:
            logger.debug(f"Extracting data from: {lead.url}")
            
            # Use robust content extractor with multiple fallback strategies
            content, extraction_method = await self.content_extractor.extract(
                url=lead.url,
                min_length=200  # Minimum viable content length
            )
            
            if not content:
                logger.warning(f"All extraction strategies failed for {lead.url}")
                grant_data = {
                    "url": lead.url,
                    "title": lead.title or "Content Extraction Failed",
                    "funder": lead.source or "Unknown",
                    "description": "⚠️ Unable to extract content from this page. Please visit the website directly to view details.",
                    "error": "All extraction methods failed (Tavily, scraping, PDF)"
                }
            else:
                # Log successful extraction with method used
                logger.info(f"✅ Content extracted via {extraction_method} ({len(content)} chars)")
                
                # Truncate content if too long
                content_preview = content[:CONTENT_PREVIEW_LENGTH]
                
                # Run extraction agent
                runner = Runner(
                    agent=self.extractor_agent,
                    app_name="grant-seeker",
                    session_service=self.session_service
                )
                
                prompt = f"Extract grant information from this webpage:\n\n{content_preview}"
                user_msg = types.Content(role="user", parts=[types.Part(text=prompt)])
                
                response_text = ""
                async for event in runner.run_async(
                    user_id="user-1",
                    session_id=session_id,
                    new_message=user_msg
                ):
                    if event.is_final_response() and event.content and event.content.parts:
                        response_text = event.content.parts[0].text
                
                
                # Parse response using Pydantic
                try:
                    # Clean up response text (remove markdown if present)
                    response_text = response_text.replace("```json", "").replace("```", "").strip()
                    
                    # Parse JSON to check if it's a list or object
                    parsed_json = json.loads(response_text)
                    
                    # Handle LIST response (multi-grant page - take first for now)
                    if isinstance(parsed_json, list):
                        if len(parsed_json) > 0:
                            logger.warning(f"Multi-grant page detected with {len(parsed_json)} grants, using first grant")
                            grant_data_obj = GrantData.model_validate(parsed_json[0])
                        else:
                            raise ValueError("LLM returned empty list")
                    # Handle OBJECT response (single grant page)
                    else:
                        grant_data_obj = GrantData.model_validate(parsed_json)
                    
                    grant_data = grant_data_obj.model_dump()
                    grant_data["url"] = lead.url
                    
                    # Check if grant_data is essentially empty (all critical fields are defaults)
                    if (grant_data["title"] == "Untitled Grant" and 
                        grant_data["deadline"] == "Not specified" and 
                        grant_data["amount"] == "Not specified" and
                        grant_data["description"] == "No description available" and
                        grant_data["funder"] == "Unknown"):
                        logger.warning(f"Extracted data appears empty for {lead.url}")
                        grant_data["error"] = "Failed to extract meaningful data"
                        
                except Exception as e:
                    logger.error(f"Failed to parse response for {lead.url}: {e}")
                    grant_data = {
                        "url": lead.url,
                        "title": lead.title or "Untitled Grant",
                        "funder": lead.source or "Unknown",
                        "error": f"Failed to parse LLM response: {str(e)}"
                    }
            
            # Fill in defaults for any missing fields
            defaults = GrantData(url=lead.url).model_dump()
            for key, value in defaults.items():
                if key not in grant_data:
                    grant_data[key] = value
            
            # Calculate fit score
            if query:
                grant_data['fit_score'] = calculate_fit_score(grant_data, query)
            
            # Cache the result
            if self.cache:
                self.cache.set(cache_key, grant_data)
            
            logger.info(f"Successfully extracted: {grant_data.get('title', 'Unknown')} (Fit: {grant_data.get('fit_score', 0)}%)")
            return grant_data
            
        except Exception as e:
            logger.error(f"Extraction failed for {lead.url}: {e}")
            return {
                "url": lead.url,
                "title": lead.title or "Untitled Grant",
                "funder": lead.source or "Unknown",
                "error": str(e),
                **GrantData(url=lead.url).model_dump()
            }
    
    async def run(self, query: str) -> list[dict]:
        """
        Run the complete grant seeking workflow.
        
        This is the main entry point called by the frontend.
        It executes the following phases:
        1. Phase 0: Generate a search query from the user's input.
        2. Phase 1: Search the web and identify promising leads.
        3. Phase 2: Extract detailed data from those leads in parallel.
        """
        logger.info(f"Starting Grant Seeker Workflow with {MODEL_NAME}")
        
        # Create main session
        main_session_id = f"main-session-{uuid.uuid4()}"
        await self.session_service.create_session(
            app_name="grant-seeker",
            user_id="user-1",
            session_id=main_session_id
        )
        
        # Phase 0: Generate Query
        logger.info("Phase 0: Generating Search Query")
        search_query = await self.generate_search_query(query)
        
        # Phase 1: Search and identify promising grants
        logger.info(f"Phase 1: Searching for Grants with query: {search_query}")
        search_results = await self.search_grants(search_query)
        
        if not search_results:
            logger.warning("No search results found")
            return []
        
        leads = await self.analyze_results(search_results, main_session_id)
        
        if not leads:
            logger.warning("No promising grants identified")
            return []
        
        # Phase 2: Extract detailed data from each grant
        logger.info(f"Phase 2: Extracting Data (Parallel Processing - {MAX_CONCURRENT_EXTRACTIONS} at a time)")
        
        # Create semaphore for controlled concurrency
        sem = asyncio.Semaphore(MAX_CONCURRENT_EXTRACTIONS)
        
        async def extract_with_semaphore(lead):
            async with sem:
                return await self.extract_grant_data(lead, query)
        
        # Process all leads concurrently
        tasks = [extract_with_semaphore(lead) for lead in leads]
        raw_results = await asyncio.gather(*tasks)
        
        # Filter expired grants and USA grants
        # Also validate URLs for 404s
        results_after_location = []
        for g in raw_results:
            if self._is_grant_expired(g) or self._is_usa_grant(g):
                continue
            
            # Verify URL is accessible
            url = g.get('url')
            if url and await self._validate_url(url):
                results_after_location.append(g)
            else:
                logger.warning(f"Excluding unreachable URL: {url}")
        
        expired_count = sum(1 for g in raw_results if self._is_grant_expired(g))
        usa_count = sum(1 for g in raw_results if self._is_usa_grant(g) and not self._is_grant_expired(g))
        logger.info(f"Filtered {expired_count} expired grants and {usa_count} USA grants")
        
        # Filter grants with insufficient data (prevent "Untitled Grant" from showing)
        results = []
        insufficient_data_grants = []
        
        for grant in results_after_location:
            if is_viable_grant(grant):
                results.append(grant)
            else:
                insufficient_data_grants.append(grant)
                logger.debug(f"Filtered grant with insufficient data: {grant.get('url', 'unknown URL')}")
        
        if insufficient_data_grants:
            logger.warning(
                f"⚠️ {len(insufficient_data_grants)} grants filtered due to insufficient data. "
                f"URLs are available but content extraction failed or returned incomplete information."
            )


        # Assign IDs
        for i, grant in enumerate(results, 1):
            grant['id'] = i
        
        logger.info("Workflow complete")
        return results

    async def run_with_minimum_results(self, query: str, filters: dict = None, min_results: int = 3):
        """
        Iteratively search until minimum RELEVANT results found.
        
        Args:
            query: User search query
            filters: Dictionary of advanced filters (optional)
            min_results: Target number of relevant grants
            
        Returns:
            List of unique, relevant, filtered grants
        """
        all_results = []
        attempted_queries = set()
        attempt = 1
        MAX_SEARCH_ATTEMPTS = 5
        
        # We need to filter results to check if we met the target.
        # However, we want to return ALL extracted data, even if it doesn't match filters?
        # No, user asked for RELEVANT results. So we should only count/return filtered ones.
        
        # Import filter logic dynamically to avoid circular import issues at toplevel
        apply_filters = None
        if filters:
            try:
                # We need to import this carefully. 
                # Since this runs in backend, we should assume we can access frontend utils
                # or better, move filter logic to a shared place.
                # For now, local import is safest.
                import sys
                import os
                # Ensure frontend path is accessible if not already
                frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
                if frontend_path not in sys.path:
                    sys.path.append(frontend_path)
                    
                from search_grants import apply_filters_to_results
                apply_filters = apply_filters_to_results
            except ImportError:
                logger.warning("Could not import apply_filters_to_results. Ignoring filters for count.")
        
        # Track seen URLs to avoid duplicates across attempts
        seen_urls = set()
        
        while len(all_results) < min_results and attempt <= MAX_SEARCH_ATTEMPTS:
            # Generate query variant
            search_query = self._generate_search_variant(query, filters, attempt)
            
            # Skip if already tried
            if search_query in attempted_queries:
                attempt += 1
                continue
            
            attempted_queries.add(search_query)
            logger.info(f"🔄 Search Attempt {attempt}/{MAX_SEARCH_ATTEMPTS}: '{search_query}' (Need {min_results}, Have {len(all_results)})")
            
            # Run extraction workflow (standard run)
            results = await self.run(search_query)
            
            # Filter duplicates immediately
            new_unique_results = []
            for grant in results:
                url = grant.get('url', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    new_unique_results.append(grant)
            
            if not new_unique_results:
                logger.info(f"   No new unique results found in attempt {attempt}")
                attempt += 1
                continue
                
            # Apply filters to check relevance
            relevant_batch = new_unique_results
            if apply_filters and filters:
                relevant_batch = apply_filters(new_unique_results, filters)
            
            count_new = len(relevant_batch)
            logger.info(f"   Found {count_new} new relevant grants in this batch")
            
            all_results.extend(relevant_batch)
            attempt += 1
            
            # Small delay to be nice to APIs
            # await asyncio.sleep(1) 
            
        logger.info(f"✅ Iterative search complete. Found {len(all_results)} total relevant grants.")
        
        # Rank by multi-factor score (Relevance + Completeness + Freshness)
        return self._rank_results(all_results, query)

    def _generate_search_variant(self, query: str, filters: dict, attempt: int) -> str:
        """Generate broader or related query variants."""
        if attempt == 1:
            return query
        
        # Attempt 2: Add specific filter keywords to query
        if attempt == 2 and filters:
            # E.g. "startup funding" -> "startup funding women"
            filter_keywords = []
            if filters.get('demographic_focus'):
                # Take first demographic keyword (e.g. "Women")
                demo = filters['demographic_focus'][0].split('/')[0].split('-')[0].strip()
                filter_keywords.append(demo)
            
            if filters.get('geographic_scope'):
                filter_keywords.append(filters['geographic_scope'])
                
            if filter_keywords:
                return f"{query} {' '.join(filter_keywords)}"
        
        # Attempt 3: Broaden - remove "grant" or "funding" if present to find other types
        if attempt == 3:
            if "grant" in query.lower():
                return query.lower().replace("grant", "funding")
            elif "funding" in query.lower():
                return query.lower().replace("funding", "grant")
        
        # Attempt 4: Simplify query (remove adjectives)
        if attempt == 4:
            # Very basic simplification strategy
            words = query.split()
            if len(words) > 2:
                # Remove shortest word (likely stopword)
                words.sort(key=len)
                return " ".join(words[1:]) # dropped shortest
            
        # Attempt 5: Fallback to very broad category
        if attempt == 5:
            base = "business grants"
            if filters and filters.get('geographic_scope'):
                 base += f" {filters['geographic_scope']}"
            else:
                 base += " Canada"
            return base
            
        return query # Fallback


    
        return query # Fallback


    async def _validate_url(self, url: str) -> bool:
        """Check if URL returns 200 OK (not 404)."""
        try:
            async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
                resp = await client.head(url)
                if resp.status_code == 404:
                    return False
                # If HEAD fails (some servers block it), try mild GET
                if resp.status_code >= 400:
                    resp = await client.get(url, headers={"Range": "bytes=0-100"}) # Fetch first 100 bytes
                    if resp.status_code == 404:
                        return False
            return True
        except Exception:
            # If checking fails (timeout etc), assume valid to be safe/permissive
            # We don't want to exclude valid sites just because they block crawlers
            return True

    def _rank_results(self, results: list, query: str) -> list:
        """
        Rank grants by multiple factors:
        1. Fit Score (Relevance) - 60%
        2. Data Completeness - 20%
        3. Freshness / Deadline Validity - 20%
        """
        scored_results = []
        
        for g in results:
            score = 0
            
            # 1. Fit Score (Relevance)
            fit = g.get('fit_score', 0)
            score += fit * 0.6
            
            # 2. Completeness
            completeness = 0
            if g.get('amount') and "not provided" not in g['amount'].lower(): completeness += 50
            if g.get('deadline') and "not specified" not in g['deadline'].lower(): completeness += 50
            score += completeness * 0.2
            
            # 3. Deadline Validity (Bonus for active dates)
            deadline = g.get('deadline', '').lower()
            if "ongoing" in deadline or "rolling" in deadline:
                score += 20 * 0.2
            elif any(c.isdigit() for c in deadline) and "expired" not in deadline:
                score += 20 * 0.2 # Specific valid date
            
            scored_results.append((score, g))
            
        # Sort desc by score
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored_results]

    def _deduplicate_results(self, results: list) -> list:
        """Remove duplicate grants based on URL."""
        seen = {}
        for r in results:
            url = r.get('url')
            if url and url not in seen:
                seen[url] = r
            elif url and url in seen:
                # Keep better fit score
                if r.get('fit_score', 0) > seen[url].get('fit_score', 0):
                    seen[url] = r
        return list(seen.values())

    
    def print_results(self, results: list[dict]) -> None:
        """Print results in a formatted manner."""
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        
        for grant in results:
            print(f"\n{'='*80}")
            print(f"Grant #{grant['id']}: {grant.get('title', 'Untitled Grant')} (Fit: {grant.get('fit_score', 0)}%)")
            print(f"{'='*80}")
            print(f"Funder: {grant.get('funder', 'Unknown')}")
            print(f"Amount: {grant.get('amount', 'Not specified')}")
            print(f"Deadline: {grant.get('deadline', 'Not specified')}")
            print(f"Geography: {grant.get('geography', 'Not specified')}")
            print(f"Funding Nature: {grant.get('funding_nature', 'Grant')}")
            print(f"\nDescription:")
            print(f"  {grant.get('description', 'No description available')}")
            print(f"\nDetailed Overview:")
            print(f"  {grant.get('detailed_overview', 'No detailed overview available')}")
            print(f"\nEligibility:")
            print(f"  {grant.get('eligibility', 'Not specified')}")
            
            # Show tags
            tags = grant.get('tags', [])
            if tags:
                print(f"\nTags: {', '.join(tags)}")

            # Show founder demographics
            demographics = grant.get('founder_demographics', [])
            if demographics:
                print(f"\nFounder Demographics: {', '.join(demographics)}")
            
            # Show application requirements
            app_reqs = grant.get('application_requirements', [])
            if app_reqs:
                print(f"\nApplication Requirements:")
                for req in app_reqs:
                    print(f"  • {req}")
            
            print(f"\nURL: {grant['url']}")
            
            if 'error' in grant:
                print(f"\n⚠️  Error: {grant['error']}")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point for the application."""
    # Create workflow
    workflow = GrantSeekerWorkflow()
    
    # Define search query
    query = "community garden grants Chicago 2025 deadline application amount funding active open"
    
    # Run workflow
    results = await workflow.run(query)
    
    # Save and print results
    workflow.print_results(results)
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
