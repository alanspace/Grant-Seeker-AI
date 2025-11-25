"""Configuration for Grant Seeker application."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv("../.env")

class Config:
    """Application configuration."""
    
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # Model Configuration
    MODEL_NAME: str = "gemini-flash-latest"
    
    # Retry Configuration
    RETRY_ATTEMPTS: int = 1
    RETRY_EXP_BASE: int = 2
    RETRY_INITIAL_DELAY: float = 1.0
    RETRY_STATUS_CODES: list[int] = [429, 500, 503, 504]
    
    # Tavily Configuration
    TAVILY_MAX_RETRIES: int = 2
    TAVILY_TIMEOUT: float = 15.0
    TAVILY_MAX_RESULTS: int = 5
    
    # Processing Configuration
    MAX_CONCURRENT_EXTRACTIONS: int = 3
    CONTENT_PREVIEW_LENGTH: int = 3000
    
    # Output Configuration
    OUTPUT_FILE: str = "grants_output.json"
    
    # Cache Configuration
    CACHE_ENABLED: bool = True
    CACHE_DIR: str = ".cache"
    CACHE_TTL_HOURS: int = 24
    
    # Session Configuration
    APP_NAME: str = "grant_seeker_direct"
    USER_ID: str = "console_user"
    MAIN_SESSION_ID: str = "main_session"
