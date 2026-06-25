"""Custom exception classes for fazle-ai-health-api."""

class LLMConnectionError(Exception):
    """Raised when the LLM API is unreachable or times out."""
    pass


class LLMResponseParseError(Exception):
    """Raised when the LLM API response cannot be parsed."""
    pass