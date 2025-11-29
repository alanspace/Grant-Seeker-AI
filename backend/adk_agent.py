"""
Grant Seeker Agent - Single file version with caching
Consolidated from refactored architecture while maintaining caching functionality
"""
import os
import asyncio
import json
import hashlib
import logging
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel
from tavily_client import TavilyClient

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
MODEL_NAME = "gemini-flash-latest"
TAVILY_MAX_RESULTS = 5
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

def clean_json_string(json_str: str) -> str:
    """Remove markdown code blocks from JSON string."""
    return json_str.replace("```json", "").replace("```", "").strip()

# ============================================================================
# CACHE SERVICE
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
            logger.error(f"Failed to cache {key}: {e}")
    
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
    funding_type: str = "Grant"
    geography: str = "Not specified"
    fit_score: int = 0

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
    """Create the grant finder agent."""
    return LlmAgent(
        name="GrantFinder",
        model=Gemini(model=MODEL_NAME, retry_options=create_retry_config()),
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
    """Create the grant extractor agent."""
    current_date, current_date_iso = get_current_date()
    
    return LlmAgent(
        name="GrantExtractor",
        model=Gemini(model=MODEL_NAME, retry_options=create_retry_config()),
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

def create_query_agent() -> LlmAgent:
    """Create the query generation agent."""
    return LlmAgent(
        name="QueryGenerator",
        model=Gemini(model=MODEL_NAME, retry_options=create_retry_config()),
        instruction="""
        You are a Search Query Expert. Your job is to convert a user's project description into a targeted search query for finding grants.
        
        Rules:
        1. Extract the core topic (e.g., "community garden", "youth education", "renewable energy").
        2. Identify the location if mentioned (e.g., "Chicago", "California").
        3. Identify the target audience (e.g., "non-profit", "schools").
        4. Combine these into a concise search query string.
        5. Add keywords like "grants", "funding", "application", "deadline".
        6. Return ONLY the query string, no other text.
        
        Example Input: "We are a non-profit in Chicago looking to build a community garden."
        Example Output: community garden grants Chicago non-profit funding application
        """
    )

# ============================================================================
# MAIN WORKFLOW
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
        
        # Initialize session service
        self.session_service = InMemorySessionService()
        
        # Create agents
        self.finder_agent = create_finder_agent()
        self.extractor_agent = create_extractor_agent()
        self.query_agent = create_query_agent()



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
            
            # Parse response
            content = response_text
            cleaned_content = clean_json_string(content)
            
            try:
                parsed = json.loads(cleaned_content)
                leads_data = DiscoveredLeadsReport(**parsed)
                logger.info(f"Identified {len(leads_data.discovered_leads)} promising grants")
                return leads_data.discovered_leads
            except (json.JSONDecodeError, Exception) as e:
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
        session_id = f"extract-{hashlib.md5(lead.url.encode()).hexdigest()[:8]}"
        await self.session_service.create_session(
            app_name="grant-seeker",
            user_id="user-1",
            session_id=session_id
        )
        
        try:
            logger.info(f"Extracting data from: {lead.url}")
            
            # Get page content
            content = await self.tavily.get_page_content(lead.url)
            
            if not content:
                logger.warning(f"No content retrieved from {lead.url}")
                grant_data = {
                    "url": lead.url,
                    "title": lead.title or "Untitled Grant",
                    "funder": lead.source or "Unknown",
                    "error": "No content retrieved"
                }
            else:
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
                
                # Parse response
                content_str = response_text
                cleaned_content = clean_json_string(content_str)
                
                try:
                    parsed = json.loads(cleaned_content)
                    
                    # Handle case where LLM returns a list instead of a dict
                    if isinstance(parsed, list):
                        if len(parsed) > 0:
                            parsed = parsed[0]
                        else:
                            parsed = {}
                    
                    # Validate and normalize the data
                    grant_data = {
                        "title": normalize_value(parsed.get("title"), "Untitled Grant"),
                        "funder": normalize_value(parsed.get("funder"), lead.source or "Unknown"),
                        "deadline": normalize_value(parsed.get("deadline"), "Not specified"),
                        "amount": normalize_value(parsed.get("amount"), "Not specified"),
                        "description": normalize_value(parsed.get("description"), "No description available"),
                        "detailed_overview": normalize_value(parsed.get("detailed_overview"), "No detailed overview available"),
                        "tags": parsed.get("tags", []),
                        "eligibility": normalize_value(parsed.get("eligibility"), "Not specified"),
                        "url": lead.url,
                        "application_requirements": parsed.get("application_requirements", []),
                        "funding_type": normalize_value(parsed.get("funding_type"), "Grant"),
                        "geography": normalize_value(parsed.get("geography"), "Not specified")
                    }
                    
                    # Check if grant_data is essentially empty (all defaults)
                    if (grant_data["title"] == "Untitled Grant" and 
                        grant_data["deadline"] == "Not specified" and 
                        grant_data["amount"] == "Not specified"):
                        logger.warning(f"Extracted data appears empty for {lead.url}")
                        grant_data["error"] = "Failed to extract meaningful data"
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error for {lead.url}: {e}")
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
        """Run the complete grant seeking workflow."""
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
        
        leads = await self.analyze_results(search_results, "main-session")
        
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
        results = await asyncio.gather(*tasks)
        
        # Assign IDs
        for i, grant in enumerate(results, 1):
            grant['id'] = i
        
        logger.info("Workflow complete")
        return results
    
    def save_results(self, results: list[dict], output_file: str = "grants_output.json") -> None:
        """Save results to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to: {output_file}")
    
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
            print(f"Funding Type: {grant.get('funding_type', 'Grant')}")
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
    workflow.save_results(results)
    workflow.print_results(results)
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
