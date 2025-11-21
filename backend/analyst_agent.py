import requests
from bs4 import BeautifulSoup
import json
import re

def analyze_grant_webpage(url):
    """
    Fetches a webpage and extracts grant-related information using best-effort keyword search.

    Args:
        url (str): The URL of the grant webpage.

    Returns:
        dict: A dictionary containing extracted information (deadline, eligibility, funding_amount, etc.).
    """
    data = {
        "url": url,
        "deadline": None,
        "eligibility": None,
        "funding_amount": None,
        "application_requirements": None
    }

    try:
        # Fetch the HTML content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an error for bad status codes
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Helper function to find text based on keywords
        def find_info(keywords):
            for keyword in keywords:
                # Search for the keyword in text nodes, case-insensitive
                element = soup.find(string=re.compile(keyword, re.IGNORECASE))
                if element:
                    parent = element.parent
                    # Clean up the text
                    text = parent.get_text(separator=' ', strip=True)
                    
                    # Heuristic: If the text is very short (likely just a label like "Deadline:"),
                    # try to get the next sibling or the parent's text to find the actual value.
                    if len(text) < 30: 
                        # Try next sibling element
                        next_sibling = parent.find_next_sibling()
                        if next_sibling:
                            return next_sibling.get_text(separator=' ', strip=True)
                        
                        # Or try the parent's parent (e.g., <div><strong>Deadline:</strong> Date</div>)
                        if parent.parent:
                            return parent.parent.get_text(separator=' ', strip=True)
                    
                    # If text is long enough, return it (truncating if it's huge to avoid returning whole page)
                    return text[:500].strip() 
            return None

        # Extract information using keywords
        data["deadline"] = find_info(["Deadline", "Due Date", "Closing Date", "Submission Date"])
        data["eligibility"] = find_info(["Eligibility", "Who can apply", "Qualifications", "Applicants"])
        data["funding_amount"] = find_info(["Funding Amount", "Grant Size", "Award Amount", "Budget", "Range"])
        data["application_requirements"] = find_info(["Application Requirements", "How to Apply", "Submission Guidelines", "Proposal Requirements"])

    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        data["error"] = f"Network error: {str(e)}"
    except Exception as e:
        print(f"Error parsing content from {url}: {e}")
        data["error"] = f"Parsing error: {str(e)}"

    return data

if __name__ == "__main__":
    # Example usage
    # Note: This is a placeholder URL. In a real scenario, use a valid grant URL.
    test_url = "https://www.example.com/grant-opportunity" 
    print(f"Analyzing {test_url}...")
    result = analyze_grant_webpage(test_url)
    print(json.dumps(result, indent=2))
