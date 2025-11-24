import json
import os
from dotenv import load_dotenv
from scout_agent import find_grant_opportunities
from analyst_agent import analyze_grant_webpage
from writer_agent import draft_proposal_section

# Load environment variables from the .env file for all agents
load_dotenv() 

def run_grant_seeker_workflow():
    """
    Simulates the full grant seeking workflow by coordinating the Scout, Analyst, and Writer agents.
    """
    print("--- Starting Grant Seeker Workflow ---")

    # Step 1: Define the project
    project_description = "Community garden for urban youth"
    print(f"\n[1] Project Description defined: {project_description}")

    # Step 2: Scout Agent - Find opportunities
    print("\n[2] Scout Agent: Searching for grant opportunities...")
    urls = find_grant_opportunities(project_description)
    
    if not urls:
        print("No opportunities found. Exiting workflow.")
        return

    print(f"Found {len(urls)} opportunities:")
    for i, url in enumerate(urls):
        print(f"  - {url}")

    # Select the first URL for this simulation
    target_url = urls[0]
    print(f"\n[3] Selected target URL: {target_url}")

    # Step 3: Analyst Agent - Analyze the webpage
    print(f"\n[4] Analyst Agent: Analyzing {target_url}...")
    grant_details = analyze_grant_webpage(target_url)
    
    print("Extracted Grant Details:")
    print(json.dumps(grant_details, indent=2))

    # Step 4: Writer Agent - Draft a proposal section
    # We'll try to use the 'application_requirements' or 'eligibility' from the analysis 
    # to form the requirement for the writer.
    
    # Fallback requirement if analysis doesn't yield specific text
    requirement_text = "Please describe how the project aligns with the grant's mission and impact goals."
    
    if grant_details.get("application_requirements"):
        requirement_text = f"Address the following application requirements: {grant_details['application_requirements']}"
    elif grant_details.get("eligibility"):
        requirement_text = f"Explain how the project meets these eligibility criteria: {grant_details['eligibility']}"

    print(f"\n[5] Writer Agent: Drafting proposal section based on requirement: '{requirement_text[:100]}...'")
    
    proposal_draft = draft_proposal_section(project_description, requirement_text)

    print("\n[6] Final Drafted Text:")
    print("-" * 40)
    print(proposal_draft)
    print("-" * 40)
    print("\n--- Workflow Completed ---")

if __name__ == "__main__":
    run_grant_seeker_workflow()
