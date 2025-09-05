"""
Validation utilities
"""
import re
from typing import Optional
from pydantic import validator
import phonenumbers
from phonenumbers import NumberParseException


def validate_phone(phone: str) -> str:
    """
    Validate phone number format
    """
    if not phone:
        raise ValueError("Phone number is required")
    
    # Remove any whitespace
    phone = phone.strip()
    
    # Check if it starts with +
    if not phone.startswith('+'):
        raise ValueError('Phone number must start with +')
    
    # Try to parse with phonenumbers library
    try:
        parsed_number = phonenumbers.parse(phone, None)
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Invalid phone number")
        return phone
    except NumberParseException:
        # Fallback to basic validation
        if not phone[1:].isdigit():
            raise ValueError('Phone number must contain only digits after +')
        if len(phone) < 10 or len(phone) > 20:
            raise ValueError('Phone number must be between 10 and 20 characters')
        return phone


def validate_email(email: str) -> str:
    """
    Validate email format
    """
    if not email:
        raise ValueError("Email is required")
    
    email = email.strip().lower()
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    return email


def validate_password(password: str) -> str:
    """
    Validate password strength
    """
    if not password:
        raise ValueError("Password is required")
    
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if len(password) > 128:
        raise ValueError("Password must be less than 128 characters")
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit")
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password must contain at least one special character")
    
    return password


def validate_name(name: str) -> str:
    """
    Validate name format
    """
    if not name:
        raise ValueError("Name is required")
    
    name = name.strip()
    
    if len(name) < 2:
        raise ValueError("Name must be at least 2 characters long")
    
    if len(name) > 150:
        raise ValueError("Name must be less than 150 characters")
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-']+$", name):
        raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
    
    return name


def validate_otp(otp: str) -> str:
    """
    Validate OTP format
    """
    if not otp:
        raise ValueError("OTP is required")
    
    otp = otp.strip()
    
    if not otp.isdigit():
        raise ValueError("OTP must contain only digits")
    
    if len(otp) != 6:
        raise ValueError("OTP must be exactly 6 digits")
    
    return otp


def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize user input
    """
    if not text:
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text
