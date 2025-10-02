"""
Validation utilities
"""
import phonenumbers
from typing import Optional


def validate_phone(phone: str, region: str = "RU") -> Optional[str]:
    """
    Validate and format phone number
    
    Args:
        phone: Phone number string
        region: Country code (default: RU)
        
    Returns:
        Formatted phone number in E164 format or None if invalid
    """
    try:
        parsed = phonenumbers.parse(phone, region)
        if phonenumbers.is_valid_number(parsed):
            return phonenumbers.format_number(
                parsed, 
                phonenumbers.PhoneNumberFormat.E164
            )
    except phonenumbers.phonenumberutil.NumberParseException:
        pass
    
    return None


def validate_email(email: str) -> bool:
    """
    Validate email address
    
    Args:
        email: Email address string
        
    Returns:
        True if valid
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
