"""Grant extractor service for extracting detailed grant information."""
import json
import logging
from typing import Optional
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from ..tavily_client import TavilyClient
from ..models import GrantData, DiscoveredLead
from ..exceptions import GrantExtractionError
from ..utils.helpers import clean_json_string, normalize_value
from ..utils.cache import CacheService

logger = logging.getLogger(__name__)


class GrantExtractorService:
    """Service for extracting detailed grant information."""
    
    def __init__(
        self,
        tavily_client: TavilyClient,
        extractor_agent: LlmAgent,
        session_service: InMemorySessionService,
        app_name: str,
        content_preview_length: int = 3000,
        cache_service: Optional[CacheService] = None
    ):
        """Initialize the grant extractor service.
        
        Args:
            tavily_client: Tavily API client
            extractor_agent: LLM agent for extracting grant data
            session_service: ADK session service
            app_name: Application name for ADK
            content_preview_length: Maximum content length to send to LLM
            cache_service: Optional cache service for page content
        """
        self.tavily = tavily_client
        self.extractor_agent = extractor_agent
        self.session_service = session_service
        self.app_name = app_name
        self.content_preview_length = content_preview_length
        self.cache = cache_service
    
    async def extract_grant_data(self, lead: DiscoveredLead) -> dict:
        """Extract detailed grant data from a lead.
        
        Args:
            lead: Discovered grant lead
            
        Returns:
            Dictionary containing extracted grant data
        """
        url = lead.url
        logger.info(f"Extracting data from: {url}")
        
        # Check cache for extracted data first
        cache_key = f"extract:{url}"
        if self.cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.info(f"Using cached extraction for: {url}")
                return cached_data
        
        try:
            # Fetch page content (also cached by Tavily client internally)
            content = await self.tavily.get_page_content(url)
            
            if not content:
                logger.warning(f"Could not fetch content for: {url}")
                return self._create_error_response(url, "Could not fetch content")
            
            # Create unique session for this extraction
            task_session_id = f"extract_{hash(url)}"
            await self.session_service.create_session(
                app_name=self.app_name,
                user_id="console_user",
                session_id=task_session_id
            )
            
            # Run extractor agent
            extractor_runner = Runner(
                agent=self.extractor_agent,
                app_name=self.app_name,
                session_service=self.session_service
            )
            
            # Pass content to extractor
            content_preview = content[:self.content_preview_length]
            msg = types.Content(
                role="user",
                parts=[types.Part(text=f"URL: {url}\n\nContent:\n{content_preview}")]
            )
            
            result_text = ""
            async for event in extractor_runner.run_async(
                user_id="console_user",
                session_id=task_session_id,
                new_message=msg
            ):
                if event.is_final_response() and event.content and event.content.parts:
                    result_text = event.content.parts[0].text
            
            # Parse and validate response
            grant_data = self._parse_extraction_result(result_text, url)
            logger.info(f"Successfully extracted data from: {url}")
            
            # Cache successful extraction
            if self.cache:
                self.cache.set(cache_key, grant_data)
            
            return grant_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error for {url}: {e}")
            return self._create_error_response(url, f"JSON parse error: {str(e)}")
        except Exception as e:
            logger.error(f"Extraction error for {url}: {e}")
            return self._create_error_response(url, str(e))
    
    def _parse_extraction_result(self, result_text: str, url: str) -> dict:
        """Parse extraction result from LLM.
        
        Args:
            result_text: Raw text from LLM
            url: Grant URL
            
        Returns:
            Parsed grant data dictionary
            
        Raises:
            json.JSONDecodeError: If JSON parsing fails
        """
        clean_json = clean_json_string(result_text)
        parsed = json.loads(clean_json)
        
        # Handle case where LLM returns a list instead of dict
        if isinstance(parsed, list):
            logger.warning(f"LLM returned list instead of dict for {url}, using first item")
            grant_data = parsed[0] if parsed else {}
        else:
            grant_data = parsed
        
        # Validate we got actual data
        if not grant_data or not isinstance(grant_data, dict):
            logger.warning(f"Empty or invalid grant data for {url}")
            grant_data = {}
        
        # Ensure all required fields exist with frontend-compatible structure
        return {
            "id": grant_data.get("id", 0),
            "title": normalize_value(grant_data.get("title"), "Untitled Grant"),
            "funder": normalize_value(grant_data.get("funder"), "Unknown"),
            "deadline": normalize_value(grant_data.get("deadline"), "Not specified"),
            "amount": normalize_value(grant_data.get("amount"), "Not specified"),
            "description": normalize_value(grant_data.get("description"), "No description available"),
            "detailed_overview": normalize_value(grant_data.get("detailed_overview"), "No detailed overview available"),
            "tags": grant_data.get("tags", []) if grant_data.get("tags") else [],
            "eligibility": normalize_value(grant_data.get("eligibility"), "Not specified"),
            "url": url,
            "application_requirements": grant_data.get("application_requirements", []) if grant_data.get("application_requirements") else [],
            "funding_type": normalize_value(grant_data.get("funding_type"), "Grant"),
            "geography": normalize_value(grant_data.get("geography"), "Not specified")
        }
    
    def _create_error_response(self, url: str, error_message: str) -> dict:
        """Create error response for failed extraction.
        
        Args:
            url: Grant URL
            error_message: Error message
            
        Returns:
            Dictionary with default values and error
        """
        return {
            "id": 0,
            "title": "Untitled Grant",
            "funder": "Unknown",
            "deadline": "Not specified",
            "amount": "Not specified",
            "description": "No description available",
            "detailed_overview": "No detailed overview available",
            "tags": [],
            "eligibility": "Not specified",
            "url": url,
            "application_requirements": [],
            "funding_type": "Grant",
            "geography": "Not specified",
            "error": error_message
        }
