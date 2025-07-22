"""
Validation utilities for Jira Agent application.

This module provides basic validation functions that are used by
the centralized ValidationService.
"""

import re
from datetime import datetime


def validate_date_format(date_string: str, format_str: str = "%Y-%m-%d") -> bool:
    """
    Validate if a date string matches the expected format.
    
    Args:
        date_string: The date string to validate
        format_str: Expected date format (default: YYYY-MM-DD)
        
    Returns:
        bool: True if date is valid, False otherwise
    """
    try:
        datetime.strptime(date_string, format_str)
        return True
    except ValueError:
        return False


def validate_issue_key_format(issue_key: str) -> bool:
    """
    Validate if a string matches Jira issue key format (e.g., PROJ-123).
    
    Args:
        issue_key: The issue key to validate
        
    Returns:
        bool: True if format is valid, False otherwise
    """
    pattern = r"^[A-Z]+[A-Z0-9]*-\d+$"
    return bool(re.match(pattern, issue_key.upper()))


def validate_time_format(time_string: str) -> bool:
    """
    Validate if a string matches Jira time format (e.g., 2h 30m, 1d, 4h).
    
    Args:
        time_string: The time string to validate
        
    Returns:
        bool: True if format is valid, False otherwise
    """
    # Jira time format patterns: 1w 2d 3h 4m (weeks, days, hours, minutes)
    pattern = r"^(\d+[wdhm]\s*)+$"
    return bool(re.match(pattern, time_string.strip(), re.IGNORECASE))


def validate_email_format(email: str) -> bool:
    """
    Validate if a string is a valid email format.
    
    Args:
        email: The email string to validate
        
    Returns:
        bool: True if format is valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def sanitize_summary(summary: str) -> str:
    """
    Sanitize issue summary by removing/replacing problematic characters.
    
    Args:
        summary: Raw summary text
        
    Returns:
        str: Sanitized summary
    """
    if not summary:
        return "Untitled Issue"
    
    # Remove excessive whitespace and limit length
    sanitized = re.sub(r'\s+', ' ', summary.strip())
    
    # Limit length to reasonable size (Jira limit is 255 chars)
    if len(sanitized) > 200:
        sanitized = sanitized[:197] + "..."
    
    return sanitized


def sanitize_description(description: str) -> str:
    """
    Sanitize issue description by cleaning up formatting.
    
    Args:
        description: Raw description text
        
    Returns:
        str: Sanitized description
    """
    if not description:
        return ""
    
    # Normalize line endings and remove excessive whitespace
    sanitized = re.sub(r'\r\n|\r', '\n', description)
    sanitized = re.sub(r'\n\s*\n\s*\n', '\n\n', sanitized)  # Remove excessive newlines
    sanitized = sanitized.strip()
    
    return sanitized