import asyncio
import logging
import sys
import os

# Add backend to path so we can import the agent
sys.path.insert(0, os.path.abspath('backend'))

from adk_agent import GrantSeekerWorkflow

# Configure logging to be clean and readable
logging.basicConfig(level=logging.ERROR) # Hide debug logs
logger = logging.getLogger("adk_agent")
logger.setLevel(logging.INFO) # Show agent info

async def run_scenario(name, query, filters, min_results=2):
    print(f"\n{'-'*80}")
    print(f"🎬 SCENARIO: {name}")
    print(f"🔎 Query: '{query}'")
    print(f"🔧 Filters: {filters}")
    print(f"{'-'*80}")
    
    workflow = GrantSeekerWorkflow()
    
    # Run the iterative search
    results = await workflow.run_with_minimum_results(
        query=query,
        filters=filters,
        min_results=min_results
    )
    
    print(f"\n✅ RESULTS FOUND: {len(results)}")
    
    for i, g in enumerate(results, 1):
        title = g.get('title', 'Unknown Title')
        fit = g.get('fit_score', 0)
        demos = g.get('founder_demographics', [])
        location = g.get('geography', 'Unknown')
        amount = g.get('amount', 'Unknown')
        valid = "✅" if g.get('url') else "❌"
        
        print(f"\n   {i}. {title}")
        print(f"      Fit Score: {fit}%")
        print(f"      Demographics: {demos}")
        print(f"      Location: {location}")
        print(f"      Amount: {amount}")
        print(f"      URL Valid: {valid}")

async def main():
    print("🚀 STARTING ADVANCED FILTER DEMO...\n")

    # 1. Women Entrepreneurs (Demographic Filter)
    await run_scenario(
        name="Women-Led Startups",
        query="startup funding Canada",
        filters={'demographic_focus': ['Women-led / Female Founders']}
    )

    # 2. Indigenous Business (Demographic Filter)
    await run_scenario(
        name="Indigenous Business Support",
        query="business loans",
        filters={'demographic_focus': ['Indigenous']}
    )

    # 3. Specific Sector (Agriculture) - No strict filter
    await run_scenario(
        name="Agriculture Tech Grants",
        query="agriculture technology",
        filters={} # No hard filters, relying on query + ranking
    )

    # 4. Ontario Only (Geographic Filter)
    await run_scenario(
        name="Ontario Tech Grants",
        query="tech grants",
        filters={'geographic_scope': 'Ontario'}
    )
    
    # 5. High Value Filter (Funding Min > $50k)
    # Note: 'funding_min' logic in backend skips grants without sufficient amount info
    await run_scenario(
        name="High Value Grants (>$50k)",
        query="business expansion grants",
        filters={'funding_min': 50000}
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user.")
