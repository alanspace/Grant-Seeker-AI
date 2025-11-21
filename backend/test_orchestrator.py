import json
from analyst_agent import analyze_grant_webpage
from writer_agent import draft_proposal_section

def run_test_workflow():
    """
    Simulates the grant seeker workflow starting from a known URL, bypassing the Scout Agent.
    """
    print("--- Starting Test Grant Seeker Workflow ---")

    # Step 1: Define the project
    project_description = "A community garden initiative in urban Chicago aiming to provide fresh produce to food deserts and educational workshops for local youth."
    print(f"\n[1] Project Description defined: {project_description}")

    # Step 2: Skip Scout Agent and use a hardcoded URL
    # Using SeedMoney as a test case
    target_url = "https://seedmoney.org/"
    print(f"\n[2] Skipped Scout Agent. Using test URL: {target_url}")

    # Step 3: Analyst Agent - Analyze the webpage
    print(f"\n[3] Analyst Agent: Analyzing {target_url}...")
    grant_details = analyze_grant_webpage(target_url)
    
    print("Extracted Grant Details:")
    print(json.dumps(grant_details, indent=2))

    if grant_details.get("error"):
        print("Analyst Agent failed. Exiting.")
        return

    # Step 4: Writer Agent - Draft a proposal section
    
    # Fallback requirement if analysis doesn't yield specific text
    requirement_text = "Please describe how the project aligns with the grant's mission and impact goals."
    
    if grant_details.get("application_requirements"):
        requirement_text = f"Address the following application requirements: {grant_details['application_requirements']}"
    elif grant_details.get("eligibility"):
        requirement_text = f"Explain how the project meets these eligibility criteria: {grant_details['eligibility']}"

    print(f"\n[4] Writer Agent: Drafting proposal section based on requirement: '{requirement_text[:100]}...'")
    
    proposal_draft = draft_proposal_section(project_description, requirement_text)

    print("\n[5] Final Drafted Text:")
    print("-" * 40)
    print(proposal_draft)
    print("-" * 40)
    print("\n--- Test Workflow Completed ---")

if __name__ == "__main__":
    run_test_workflow()
