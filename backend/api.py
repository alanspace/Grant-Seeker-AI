# api.py
import os
from dotenv import load_dotenv
from scout_agent import find_grant_opportunities
from analyst_agent import analyze_grant_webpage
from writer_agent import draft_proposal_section

# Load env vars so Ujjwal doesn't have to worry about it
load_dotenv()

# A simple in-memory cache so we don't re-scrape the same URL 5 times
grant_cache = {}

def find_grants(project_description):
    """
    Front-end calls this to get a list of grants.
    """
    print(f"API CALL: Finding grants for: {project_description}")
    urls = find_grant_opportunities(project_description)
    
    # Transform simple URLs into a structure the UI can use
    structured_results = []
    for i, url in enumerate(urls):
        grant_id = str(i) # Simple ID for now
        grant_obj = {
            "id": grant_id,
            "url": url,
            "title": f"Grant Opportunity #{i+1}", # We could use AI to get real titles later
            "summary": "Click 'Analyze' to see details."
        }
        structured_results.append(grant_obj)
        
        # Save to cache so we can look it up later by ID
        grant_cache[grant_id] = grant_obj
        
    return structured_results

def get_grant_details(grant_id):
    """
    Front-end calls this when user clicks 'Analyze' on a specific grant.
    """
    print(f"API CALL: Analyzing grant ID: {grant_id}")
    
    if grant_id not in grant_cache:
        return {"error": "Grant ID not found"}
    
    # Get the URL from our cache
    target_url = grant_cache[grant_id]['url']
    
    # Call the Analyst Agent
    details = analyze_grant_webpage(target_url)
    
    # Return the raw details to the UI
    return details

def draft_proposal(project_description, grant_details):
    """
    Front-end calls this to generate the final text.
    """
    print("API CALL: Drafting proposal...")
    
    # 1. Construct the requirement string from the analysis
    requirement_text = "Please describe how the project aligns with the grant's mission."
    if grant_details.get("application_requirements"):
        requirement_text = f"Address the following requirements: {grant_details['application_requirements']}"
    elif grant_details.get("eligibility"):
        requirement_text = f"Explain how the project meets these eligibility criteria: {grant_details['eligibility']}"

    # 2. Call the Writer Agent
    final_text = draft_proposal_section(project_description, requirement_text)
    
    return final_text