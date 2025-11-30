"""Custom exceptions for Grant Seeker application."""


class GrantSeekerError(Exception):
    """Base exception for Grant Seeker application."""
    pass


class GrantSearchError(GrantSeekerError):
    """Exception raised when grant search fails."""
    pass


class GrantExtractionError(GrantSeekerError):
    """Exception raised when grant extraction fails."""
    pass


class LeadParsingError(GrantSeekerError):
    """Exception raised when parsing discovered leads fails."""
    pass
