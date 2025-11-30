"""Grant finder service for discovering grant opportunities."""
import json
import logging
from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from tavily_client import TavilyClient
from models import DiscoveredLead
from exceptions import GrantSearchError, LeadParsingError
from utils.helpers import clean_json_string
from utils.cache import CacheService

logger = logging.getLogger(__name__)


class GrantFinderService:
    """Service for finding grant opportunities."""
    
    def __init__(
        self,
        tavily_client: TavilyClient,
        finder_agent: LlmAgent,
        session_service: InMemorySessionService,
        app_name: str,
        max_results: int = 5,
        cache_service: Optional[CacheService] = None
    ):
        """Initialize the grant finder service.
        
        Args:
            tavily_client: Tavily API client
            finder_agent: LLM agent for analyzing search results
            session_service: ADK session service
            app_name: Application name for ADK
            max_results: Maximum number of search results
            cache_service: Optional cache service for search results
        """
        self.tavily = tavily_client
        self.finder_agent = finder_agent
        self.session_service = session_service
        self.app_name = app_name
        self.max_results = max_results
        self.cache = cache_service
    
    async def search_grants(self, query: str) -> list[dict]:
        """Search for grants using Tavily API with caching.
        
        Args:
            query: Search query string
            
        Returns:
            List of search results
            
        Raises:
            GrantSearchError: If search fails
        """
        # Check cache first
        cache_key = f"search:{query}:{self.max_results}"
        if self.cache:
            cached_results = self.cache.get(cache_key)
            if cached_results is not None:
                logger.info(f"Using cached search results for: {query}")
                return cached_results
        
        # Perform search
        try:
            logger.info(f"Searching for grants with query: {query}")
            results = await self.tavily.search(query, max_results=self.max_results)
            logger.info(f"Found {len(results)} search results")
            
            # Cache results
            if self.cache:
                self.cache.set(cache_key, results)
            
            return results
        except Exception as e:
            logger.error(f"Grant search failed: {e}")
            raise GrantSearchError(f"Failed to search for grants: {e}")
    
    def _format_search_results(self, results: list[dict]) -> str:
        """Format search results for LLM agent.
        
        Args:
            results: List of search results
            
        Returns:
            Formatted string of search results
        """
        summary = "Here are the search results:\n\n"
        for i, result in enumerate(results, 1):
            summary += f"{i}. {result.get('title', 'No title')}\n"
            summary += f"   URL: {result.get('url', '')}\n"
            summary += f"   Snippet: {result.get('content', '')[:200]}...\n\n"
        return summary
    
    async def analyze_results(
        self,
        search_results: list[dict],
        session_id: str
    ) -> list[DiscoveredLead]:
        """Analyze search results to identify promising grants.
        
        Args:
            search_results: List of search results
            session_id: Session ID for ADK
            
        Returns:
            List of discovered grant leads
            
        Raises:
            LeadParsingError: If parsing leads fails
        """
        logger.info("Analyzing search results with LLM agent")
        
        # Format results for agent
        search_summary = self._format_search_results(search_results)
        
        # Run finder agent
        finder_runner = Runner(
            agent=self.finder_agent,
            app_name=self.app_name,
            session_service=self.session_service
        )
        
        user_msg = types.Content(role="user", parts=[types.Part(text=search_summary)])
        
        leads_json_str = ""
        async for event in finder_runner.run_async(
            user_id="console_user",
            session_id=session_id,
            new_message=user_msg
        ):
            if event.is_final_response() and event.content and event.content.parts:
                leads_json_str = event.content.parts[0].text
        
        # Parse leads
        try:
            clean_json = clean_json_string(leads_json_str)
            leads_data = json.loads(clean_json)
            
            if isinstance(leads_data, dict) and "discovered_leads" in leads_data:
                leads_list = leads_data["discovered_leads"]
            elif isinstance(leads_data, list):
                leads_list = leads_data
            else:
                leads_list = []
            
            # Convert to Pydantic models
            leads = [DiscoveredLead(**lead) for lead in leads_list]
            logger.info(f"Identified {len(leads)} promising grants")
            return leads
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse leads JSON: {e}")
            logger.debug(f"Raw output: {leads_json_str}")
            raise LeadParsingError(f"Failed to parse leads: {e}")
        except Exception as e:
            logger.error(f"Error processing leads: {e}")
            raise LeadParsingError(f"Error processing leads: {e}")
