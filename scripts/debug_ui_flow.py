"""Debug script: simulate the exact execute_grant_workflow path used by the UI."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()

import asyncio
from backend import adk_agent

def execute_grant_workflow(query, filters=None, min_results=3):
    workflow = adk_agent.GrantSeekerWorkflow()
    results = []
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        if min_results > 1:
            results = loop.run_until_complete(
                workflow.run_with_minimum_results(query, filters=filters, min_results=min_results)
            )
        else:
            results = loop.run_until_complete(workflow.run(query))
    except Exception as e:
        print(f"EXCEPTION in execute_grant_workflow: {e}")
        import traceback; traceback.print_exc()
    finally:
        loop.close()
        asyncio.set_event_loop(None)
    return results

results = execute_grant_workflow("Canadian technology grant", min_results=3)
print(f"\nResults: {len(results)}")
for r in results[:5]:
    print(f"  - {r.get('title', '??')} | fit={r.get('fit_score', 0)}%")
