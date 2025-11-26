"""
Grant Seeker Agent - Refactored with clean architecture
This version uses direct Tavily API with proper separation of concerns
"""
import asyncio
import json
import logging
from google.adk.sessions import InMemorySessionService

from config import Config
from tavily_client import TavilyClient
from agents import create_finder_agent, create_extractor_agent
from services.grant_finder import GrantFinderService
from services.grant_extractor import GrantExtractorService
from utils.cache import CacheService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GrantSeekerWorkflow:
    """Main workflow orchestrator for grant seeking."""
    
    def __init__(self):
        """Initialize the grant seeker workflow."""
        # Initialize cache service
        self.cache = None
        if Config.CACHE_ENABLED:
            self.cache = CacheService(
                cache_dir=Config.CACHE_DIR,
                ttl_hours=Config.CACHE_TTL_HOURS
            )
        
        # Initialize Tavily client
        self.tavily = TavilyClient(
            api_key=Config.TAVILY_API_KEY,
            max_retries=Config.TAVILY_MAX_RETRIES,
            timeout=Config.TAVILY_TIMEOUT
        )
        
        # Initialize session service
        self.session_service = InMemorySessionService()
        
        # Create agents
        self.finder_agent = create_finder_agent()
        self.extractor_agent = create_extractor_agent()
        
        # Initialize services
        self.finder_service = GrantFinderService(
            tavily_client=self.tavily,
            finder_agent=self.finder_agent,
            session_service=self.session_service,
            app_name=Config.APP_NAME,
            max_results=Config.TAVILY_MAX_RESULTS,
            cache_service=self.cache
        )
        
        self.extractor_service = GrantExtractorService(
            tavily_client=self.tavily,
            extractor_agent=self.extractor_agent,
            session_service=self.session_service,
            app_name=Config.APP_NAME,
            content_preview_length=Config.CONTENT_PREVIEW_LENGTH,
            cache_service=self.cache
        )
    
    async def run(self, query: str) -> list[dict]:
        """Run the complete grant seeking workflow.
        
        Args:
            query: Search query for grants
            
        Returns:
            List of extracted grant data dictionaries
        """
        logger.info(f"Starting Grant Seeker Workflow with {Config.MODEL_NAME}")
        
        # Create main session
        await self.session_service.create_session(
            app_name=Config.APP_NAME,
            user_id=Config.USER_ID,
            session_id=Config.MAIN_SESSION_ID
        )
        
        # Phase 1: Search and identify promising grants
        logger.info("Phase 1: Searching for Grants")
        search_results = await self.finder_service.search_grants(query)
        
        if not search_results:
            logger.warning("No search results found")
            return []
        
        leads = await self.finder_service.analyze_results(
            search_results,
            Config.MAIN_SESSION_ID
        )
        
        if not leads:
            logger.warning("No promising grants identified")
            return []
        
        # Phase 2: Extract detailed data from each grant
        logger.info(f"Phase 2: Extracting Data (Parallel Processing - {Config.MAX_CONCURRENT_EXTRACTIONS} at a time)")
        
        # Create semaphore for controlled concurrency
        sem = asyncio.Semaphore(Config.MAX_CONCURRENT_EXTRACTIONS)
        
        async def extract_with_semaphore(lead):
            async with sem:
                return await self.extractor_service.extract_grant_data(lead)
        
        # Process all leads concurrently
        tasks = [extract_with_semaphore(lead) for lead in leads]
        results = await asyncio.gather(*tasks)
        
        # Assign IDs
        for i, grant in enumerate(results, 1):
            grant['id'] = i
        
        logger.info("Workflow complete")
        return results
    
    def save_results(self, results: list[dict], output_file: str = None) -> None:
        """Save results to JSON file.
        
        Args:
            results: List of grant data dictionaries
            output_file: Output file path (defaults to Config.OUTPUT_FILE)
        """
        output_file = output_file or Config.OUTPUT_FILE
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_file}")
    
    def print_results(self, results: list[dict]) -> None:
        """Print results in a formatted manner.
        
        Args:
            results: List of grant data dictionaries
        """
        print("\n" + "="*80)
        print("FINAL RESULTS")
        print("="*80)
        
        for grant in results:
            print(f"\n{'='*80}")
            print(f"Grant #{grant['id']}: {grant.get('title', 'Untitled Grant')}")
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
