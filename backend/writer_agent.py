import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

def draft_proposal_section(project_details, grant_requirements):
    """
    Drafts a section of a grant proposal using the Gemini model.

    Args:
        project_details (str): Details about the project.
        grant_requirements (str): Specific requirements for the grant section.

    Returns:
        str: The generated proposal section text.
    """
    
    # Retrieve GEMINI_API_KEY from environment variables
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in .env file.")
        return ""

    # Configure the Gemini API
    # We need to configure the library with the API key to authenticate our requests.
    genai.configure(api_key=GEMINI_API_KEY)

    # Initialize the model
    # We use 'gemini-pro' (or a similar available model) for text generation.
    # model = genai.GenerativeModel('gemini-pro')
    model = genai.GenerativeModel('gemini-pro-latest')
    
    # Construct the prompt
    # Prompt engineering is crucial here. We instruct the model to adopt a specific persona 
    # (professional grant writer) and provide clear context (project details) and a specific goal (grant requirements).
    prompt = f"""
    You are an expert professional grant writer with a track record of securing funding for non-profit projects.
    
    Your task is to write a specific section of a grant proposal based on the following information:
    
    PROJECT DETAILS:
    {project_details}
    
    SECTION REQUIREMENTS:
    {grant_requirements}
    
    Please write a compelling, well-structured, and persuasive response that directly addresses the requirements using the project details provided. 
    Ensure the tone is professional, inspiring, and aligned with standard grant writing practices.
    """

    try:
        # Generate content
        # We send the prompt to the model to generate the response.
        response = model.generate_content(prompt)

        # Return the text
        # We extract the text from the response object.
        return response.text
    except Exception as e:
        print(f"An error occurred during generation: {e}")
        print("Falling back to mock proposal text for demonstration purposes.")
        return f"""
        [MOCK PROPOSAL SECTION]
        
        Project Title: {project_details[:50]}...
        
        Response to Requirements:
        Our community garden initiative directly addresses the grant's mission by transforming underutilized urban spaces into vibrant hubs of food production and education. By providing fresh, organic produce to food deserts in Chicago, we tackle food insecurity head-on. Furthermore, our educational workshops empower local youth with sustainable gardening skills, fostering a new generation of environmental stewards. This project aligns perfectly with your goal of supporting community-led sustainable agriculture and health initiatives.
        """

if __name__ == "__main__":
    # Example usage
    details = "A community garden project in downtown aiming to provide fresh produce to low-income families and educational workshops for youth."
    reqs = "Describe the impact of your project on the local community."
    proposal_text = draft_proposal_section(details, reqs)
    print("Drafted Proposal Section:")
    print(proposal_text)
