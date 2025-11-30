from dotenv import load_dotenv
import os

load_dotenv()

cx = os.getenv("SEARCH_ENGINE_ID")
print(f"SEARCH_ENGINE_ID='{cx}'")
