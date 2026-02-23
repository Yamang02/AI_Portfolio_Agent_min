"""Custom exception classes for the application"""


class LLMServiceError(Exception):
    """Raised when LLM service encounters an error"""
    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded"""
    pass


class ValidationError(Exception):
    """Raised when input/output validation fails"""
    pass
