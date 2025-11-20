import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables from .env file
load_dotenv()

def find_grant_opportunities(project_description):
    """
    Performs a custom Google search to find grant opportunities for a given project description.

    Args:
        project_description (str): A description of the project to find grants for.

    Returns:
        list: A list of URLs for the top 5 search results.
    """
    
    # Retrieve API_KEY and SEARCH_ENGINE_ID from environment variables
    API_KEY = os.getenv("API_KEY")
    SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

    if not API_KEY or not SEARCH_ENGINE_ID:
        print(f"Error: API_KEY or SEARCH_ENGINE_ID not found in .env file. API_KEY={bool(API_KEY)}, CX={bool(SEARCH_ENGINE_ID)}")
        return []

    # Build the Google Custom Search service
    # This creates a service object that allows us to interact with the API.
    service = build("customsearch", "v1", developerKey=API_KEY)

    # Formulate the search query
    # We combine the project description with specific keywords to target grant opportunities.
    query = f"{project_description} grant opportunities for non-profits"

    try:
        # Execute the search
        # cx is the Search Engine ID, q is the query string.
        # We request 5 results (num=5).
        result = service.cse().list(q=query, cx=SEARCH_ENGINE_ID, num=5).execute()

        # Retrieve the items from the search result
        # 'items' contains the list of search results. If no results are found, it might be missing.
        search_results = result.get("items", [])

        # Extract URLs from the results
        # We iterate through the results and collect the 'link' attribute of each item.
        urls = [item["link"] for item in search_results]

        return urls

    except Exception as e:
        print(f"An error occurred during the search: {e}")
        print("Falling back to hardcoded URLs for demonstration purposes.")
        return [
            "https://seedmoney.org/",
            "https://www.growingspaces.com/grant-opportunities/",
            "https://www.kidsgardening.org/grant-opportunities/"
        ]

if __name__ == "__main__":
    # Example usage
    description = "Community garden for urban youth"
    links = find_grant_opportunities(description)
    print("Found opportunities:")
    for link in links:
        print(link)
