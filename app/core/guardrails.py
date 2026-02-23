"""Input/output validation and filtering guardrails"""

import re
from app.core.exceptions import ValidationError


# XSS and script injection patterns
DANGEROUS_PATTERNS = [
    r"<script[^>]*>.*?</script>",  # Script tags
    r"javascript:",  # JavaScript URLs
    r"on\w+\s*=",  # Event handlers (onclick, onload, etc.)
    r"eval\s*\(",  # eval() function
    r"expression\s*\(",  # CSS expressions
    r"<iframe[^>]*>",  # iframes
    r"<object[^>]*>",  # object tags
    r"<embed[^>]*>",  # embed tags
    r"document\.",  # document access
    r"window\.",  # window access
]


def validate_input(text: str, max_length: int = 10000) -> str:
    """
    Validate and filter user input for XSS/injection attacks
    
    Args:
        text: User input to validate
        max_length: Maximum allowed input length
        
    Returns:
        Cleaned input text
        
    Raises:
        ValidationError: If input contains dangerous patterns or exceeds limits
    """
    if not isinstance(text, str):
        raise ValidationError("Input must be a string")
    
    if not text.strip():
        raise ValidationError("Input cannot be empty or whitespace-only")
    
    if len(text) > max_length:
        raise ValidationError(f"Input exceeds maximum length of {max_length} characters")
    
    # Check for dangerous patterns (case-insensitive)
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            raise ValidationError(f"Input contains potentially dangerous content")
    
    return text.strip()


def validate_output(text: str) -> str:
    """
    Validate and clean LLM output
    
    Args:
        text: LLM output to validate
        
    Returns:
        Validated output text
        
    Raises:
        ValidationError: If output is empty or invalid
    """
    if not isinstance(text, str):
        raise ValidationError("Output must be a string")
    
    cleaned = text.strip()
    
    if not cleaned:
        raise ValidationError("LLM returned empty response")
    
    return cleaned
