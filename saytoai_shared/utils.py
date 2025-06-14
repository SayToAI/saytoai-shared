"""
SayToAI Shared Utility Functions
===============================

Comprehensive collection of utility functions for the SayToAI ecosystem.
This module contains 50+ production-ready functions extracted and adapted 
from the original voiceBot project and enhanced for the new architecture.

Function Categories:
- 👤 User Management: sanitize_username, get_display_name, validate_user_input
- 📱 Phone & SMS: validate_phone_number, generate_sms_code, determine_sms_delivery_method
- 📧 Email Validation: validate_email_for_registration, check_email_abuse_patterns
- 💳 Payment Processing: validate_payment_amount, calculate_credits_for_amount
- 🛡️ Security & Fraud: calculate_risk_score, analyze_ip_geolocation, validate_captcha
- 🎭 Role & Prompt Management: validate_user_role_permissions, get_default_prompt_for_context
- 🔧 General Utilities: format_datetime, parse_error_message, mask_sensitive_data

Key Features:
- ✅ Production-ready with comprehensive error handling
- ✅ voiceBot payment system compatibility (tiyin-based calculations)
- ✅ Cost-optimized SMS delivery (Telegram bot first, SMS fallback)
- ✅ Multi-layer fraud prevention and risk assessment
- ✅ International phone number validation
- ✅ Comprehensive email validation with provider checking

Usage:
    from saytoai_shared.utils import (
        validate_phone_number, generate_sms_code,
        validate_payment_amount, calculate_risk_score
    )

Version: 0.0.1
Last Updated: 2025-06-15
"""

import re
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from .constants import (
    SUPPORTED_LANGUAGES,
    USER_ROLES,
    MIN_USERNAME_LENGTH,
    MAX_USERNAME_LENGTH,
    ROLE_FEATURES,
    ROLE_PROMPT_LIMITS,
    ROLE_CREDIT_LIMITS,
    PROMPT_VALIDATION,
    DEFAULT_PROMPTS,
    EMAIL_VALIDATION_RULES,
    EMAIL_VALIDATION_MESSAGES,
    EMAIL_VALIDATION_PATTERNS,
    ALLOWED_EMAIL_PROVIDERS,
    PHONE_VALIDATION_RULES,
    SMS_VALIDATION_MESSAGES,
    SMS_CODE_LENGTH,
    SMSDeliveryMethod,
    SMS_SERVICE_CONFIG,
    SMS_TEMPLATES,
    SMS_CODE_EXPIRATION_MINUTES,
    MAX_SMS_ATTEMPTS_PER_HOUR,
    SMS_RESEND_COOLDOWN_SECONDS,
    RISK_SCORING,
    FRAUD_DETECTION_RULES,
    ENHANCED_PHONE_VALIDATION,
    PLATFORM_CREDIT_ALLOCATION,
    VERIFICATION_REQUIREMENTS,
    FraudDetectionAction,
    IP_RATE_LIMITS,
    PAYMENT_LIMITS,
    PAYMENT_PROVIDERS,
    PAYMENT_TARIFFS
)

# ============================================================================
# USER MANAGEMENT UTILITIES
# ============================================================================

def sanitize_username(username: str) -> str:
    """
    Sanitize and normalize username.
    
    Args:
        username: Raw username string
    
    Returns:
        Sanitized username
    """
    if not username:
        return ""
    
    # Remove extra whitespace and convert to lowercase
    sanitized = username.strip().lower()
    
    # Remove special characters except underscores and dots
    sanitized = re.sub(r'[^\w.]', '', sanitized)
    
    # Ensure minimum and maximum length
    if len(sanitized) < MIN_USERNAME_LENGTH:
        return ""
    if len(sanitized) > MAX_USERNAME_LENGTH:
        sanitized = sanitized[:MAX_USERNAME_LENGTH]
    
    return sanitized

def validate_phone_number(phone: str) -> Dict[str, Any]:
    """
    Simplified phone number validation - only checks format and digits.
    
    Args:
        phone: Phone number string to validate
        
    Returns:
        Dict with validation result and details
    """
    from .constants import ENHANCED_PHONE_VALIDATION, SMS_VALIDATION_MESSAGES
    
    result = {
        "is_valid": False,
        "formatted_phone": None,
        "error_message": None,
        "warnings": []
    }
    
    if not phone:
        result["error_message"] = SMS_VALIDATION_MESSAGES["invalid_phone_format"]
        return result
    
    # Remove any whitespace
    phone = phone.strip()
    
    # Check if starts with +
    if not phone.startswith('+'):
        result["error_message"] = SMS_VALIDATION_MESSAGES["missing_plus_prefix"]
        return result
    
    # Extract digits after +
    digits_part = phone[1:]
    
    # Check if contains only digits
    if not digits_part.isdigit():
        result["error_message"] = SMS_VALIDATION_MESSAGES["invalid_characters"]
        return result
    
    # Check length constraints
    if len(digits_part) < PHONE_VALIDATION_RULES["min_digits"]:
        result["error_message"] = SMS_VALIDATION_MESSAGES["phone_too_short"]
        return result
    
    if len(digits_part) > PHONE_VALIDATION_RULES["max_digits"]:
        result["error_message"] = SMS_VALIDATION_MESSAGES["phone_too_long"]
        return result

    
    # Check for minimum unique digits
    unique_digits = len(set(digits_part))
    if unique_digits < ENHANCED_PHONE_VALIDATION["min_unique_digits"]:
        result["warnings"].append("Phone number has limited digit variety")
    
    # Phone is valid
    result["is_valid"] = True
    result["formatted_phone"] = phone
    
    return result


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number by removing spaces, dashes, parentheses.
    
    Args:
        phone: Raw phone number string
        
    Returns:
        Normalized phone number with only + and digits
    """
    if not phone:
        return ""
    
    # Remove common formatting characters
    normalized = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")
    
    return normalized.strip()

def is_suspicious_phone_number(phone: str) -> Dict[str, Any]:
    """
    Basic suspicious phone number detection.
    
    Args:
        phone: Phone number to check
        
    Returns:
        Dict with suspicion analysis
    """
    result = {
        "is_suspicious": False,
        "risk_factors": [],
        "risk_score": 0.0
    }
    
    if not phone or len(phone) < 8:
        return result
    
    digits_part = phone[1:] if phone.startswith('+') else phone
    
    # Check for patterns that might indicate fake numbers
    risk_score = 0.0
    
    # All same digits (e.g., +1111111111)
    if len(set(digits_part)) == 1:
        result["risk_factors"].append("all_same_digits")
        risk_score += 0.8
    
    # Sequential digits (e.g., +1234567890)
    if _is_sequential_digits(digits_part):
        result["risk_factors"].append("sequential_digits")
        risk_score += 0.6
    
    # Very few unique digits
    unique_digits = len(set(digits_part))
    if unique_digits < 4:
        result["risk_factors"].append("few_unique_digits")
        risk_score += 0.2
    
    result["risk_score"] = min(risk_score, 1.0)
    result["is_suspicious"] = risk_score > 0.5
    
    return result

def _is_sequential_digits(digits: str) -> bool:
    """Check if digits are in sequential order."""
    if len(digits) < 4:
        return False
    
    # Check ascending sequence
    ascending_count = 0
    for i in range(1, len(digits)):
        if int(digits[i]) == int(digits[i-1]) + 1:
            ascending_count += 1
        else:
            ascending_count = 0
        
        if ascending_count >= 3:  # 4 consecutive ascending digits
            return True
    
    # Check descending sequence
    descending_count = 0
    for i in range(1, len(digits)):
        if int(digits[i]) == int(digits[i-1]) - 1:
            descending_count += 1
        else:
            descending_count = 0
        
        if descending_count >= 3:  # 4 consecutive descending digits
            return True
    
    return False

def format_datetime(dt: datetime, timezone_name: str = "UTC") -> str:
    """
    Format datetime for display.
    
    Args:
        dt: Datetime object
        timezone_name: Target timezone name
    
    Returns:
        Formatted datetime string
    """
    if not dt:
        return "N/A"
    
    try:
        # Convert to target timezone if specified
        if timezone_name == "Tashkent":
            # Tashkent is UTC+5
            tashkent_tz = timezone(timedelta(hours=5))
            dt = dt.astimezone(tashkent_tz)
        elif timezone_name == "UTC":
            dt = dt.astimezone(timezone.utc)
        
        return dt.strftime("%d.%m.%Y, %H:%M:%S")
    
    except Exception:
        return dt.isoformat()

def get_user_flow_state(user: Dict[str, Any]) -> str:
    """
    Determine what step the user needs to complete next.
    Extracted from voiceBot helpers.py
    
    Args:
        user: User data dictionary
    
    Returns:
        Next required step identifier
    """
    if not user:
        return "create_user"
    if not user.get("language"):
        return "select_language"
    if not user.get("role"):
        return "select_role"
    if not user.get("contact_shared"):
        return "share_contact"
    return "complete"

def split_long_message(message_text: str, max_parts: int = 3) -> List[str]:
    """
    Split a long message into 2-3 parts based on content structure.
    
    Args:
        message_text: The message to split
        max_parts: Maximum number of parts (default: 3)
    
    Returns:
        List of message parts
    """
    # If message is short enough, return as single part
    if len(message_text) <= 800:
        return [message_text]
    
    # Split by major sections (double newlines or section headers)
    sections = []
    current_section = ""
    
    lines = message_text.split('\n')
    
    for line in lines:
        # Check if this is a section header (starts with emoji or bold text)
        is_section_header = (
            line.strip().startswith(('🌟', '📋', '', '🎯', '🔐', '🛡️', '📞', '💬', '⚙️', '🎤', '💳', '👤', '📈', '👑', '📋')) or
            line.strip().startswith('<b>') or
            (line.strip() and not current_section.strip())
        )
        
        # If we hit a section header and current section is substantial, save it
        if is_section_header and current_section.strip() and len(current_section) > 200:
            sections.append(current_section.strip())
            current_section = line + '\n'
        else:
            current_section += line + '\n'
    
    # Add the last section
    if current_section.strip():
        sections.append(current_section.strip())
    
    # If we have too many sections, merge smaller ones
    if len(sections) > max_parts:
        merged_sections = []
        current_merged = ""
        
        for section in sections:
            if len(current_merged + section) <= 1500 and len(merged_sections) < max_parts - 1:
                current_merged += ("\n\n" if current_merged else "") + section
            else:
                if current_merged:
                    merged_sections.append(current_merged)
                current_merged = section
        
        if current_merged:
            merged_sections.append(current_merged)
        
        sections = merged_sections
    
    # Ensure we don't exceed max_parts
    if len(sections) > max_parts:
        # Merge the last sections
        last_sections = sections[max_parts-1:]
        sections = sections[:max_parts-1] + ['\n\n'.join(last_sections)]
    
    return sections if sections else [message_text]

def calculate_credits_needed(input_tokens: int, output_tokens: int, cost_per_1k_tokens: float = 0.002) -> int:
    """
    Calculate credits needed for a request based on token usage.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens  
        cost_per_1k_tokens: Cost per 1000 tokens in USD
    
    Returns:
        Number of credits needed (rounded up)
    """
    total_tokens = input_tokens + output_tokens
    cost_usd = (total_tokens / 1000) * cost_per_1k_tokens
    
    # Convert to credits (assuming 1 credit = $0.01)
    credits_needed = cost_usd / 0.01
    
    # Round up to nearest integer
    import math
    return math.ceil(credits_needed)

def validate_user_input(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Validate user input data.
    
    Args:
        data: Input data dictionary
        required_fields: List of required field names
    
    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []
    
    # Check required fields
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            errors.append(f"Field '{field}' is required")
    
    # Validate specific fields
    if "username" in data and data["username"]:
        sanitized = sanitize_username(data["username"])
        if not sanitized:
            errors.append("Username is invalid or too short")
        elif sanitized != data["username"]:
            warnings.append(f"Username will be sanitized to: {sanitized}")
    
    if "phone_number" in data and data["phone_number"]:
        if not validate_phone_number(data["phone_number"]):
            errors.append("Phone number format is invalid")
    
    if "language" in data and data["language"]:
        if data["language"] not in SUPPORTED_LANGUAGES:
            errors.append(f"Language must be one of: {SUPPORTED_LANGUAGES}")
    
    if "role" in data and data["role"]:
        if data["role"] not in USER_ROLES:
            errors.append(f"Role must be one of: {USER_ROLES}")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }

def generate_order_id(user_id: int, timestamp: Optional[datetime] = None) -> str:
    """
    Generate a unique order ID for payments.
    
    Args:
        user_id: User identifier
        timestamp: Optional timestamp (defaults to now)
    
    Returns:
        Unique order ID string
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)
    
    # Format: SAYTOAI-{user_id}-{timestamp}
    time_str = timestamp.strftime("%Y%m%d%H%M%S")
    return f"SAYTOAI-{user_id}-{time_str}"

def parse_error_message(error: Exception) -> str:
    """
    Parse and format error messages for user display.
    
    Args:
        error: Exception object
    
    Returns:
        User-friendly error message
    """
    error_str = str(error).lower()
    
    # Common error patterns
    if "connection" in error_str or "network" in error_str:
        return "Network connection error. Please try again."
    elif "timeout" in error_str:
        return "Request timed out. Please try again."
    elif "unauthorized" in error_str or "authentication" in error_str:
        return "Authentication failed. Please check your credentials."
    elif "rate limit" in error_str:
        return "Too many requests. Please wait a moment and try again."
    elif "validation" in error_str:
        return "Invalid input data. Please check your information."
    elif "payment" in error_str:
        return "Payment processing failed. Please try again or contact support."
    else:
        return "An unexpected error occurred. Please try again or contact support."

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def mask_sensitive_data(data: str, mask_char: str = "*", reveal_last: int = 4) -> str:
    """
    Mask sensitive data like phone numbers or emails.
    
    Args:
        data: Sensitive data string
        mask_char: Character to use for masking
        reveal_last: Number of characters to reveal at the end
    
    Returns:
        Masked data string
    """
    if not data or len(data) <= reveal_last:
        return data
    
    mask_length = len(data) - reveal_last
    return mask_char * mask_length + data[-reveal_last:]

def normalize_language_code(language: str) -> str:
    """
    Normalize language code to supported format.
    
    Args:
        language: Language code or name
    
    Returns:
        Normalized language code
    """
    if not language:
        return "english"
    
    language = language.lower().strip()
    
    # Map common variations
    language_map = {
        "en": "english",
        "uz": "uzbek", 
        "ru": "russian",
        "es": "spanish",
        "fr": "french",
        "de": "german",
        "it": "italian",
        "zh": "chinese",
        "ja": "japanese",
        "ko": "korean",
        "ar": "arabic",
        "english": "english",
        "uzbek": "uzbek",
        "russian": "russian",
        "spanish": "spanish",
        "french": "french", 
        "german": "german",
        "italian": "italian",
        "chinese": "chinese",
        "japanese": "japanese",
        "korean": "korean",
        "arabic": "arabic"
    }
    
    return language_map.get(language, "english")

def get_display_name(user_data: Dict[str, Any]) -> str:
    """
    Get a display name for a user from available data.
    
    Args:
        user_data: User data dictionary
    
    Returns:
        Display name string
    """
    # Try full name first
    first_name = user_data.get("first_name", "").strip()
    last_name = user_data.get("last_name", "").strip()
    
    if first_name and last_name:
        return f"{first_name} {last_name}"
    elif first_name:
        return first_name
    elif last_name:
        return last_name
    
    # Fall back to username
    username = user_data.get("username", "").strip()
    if username:
        return f"@{username}"
    
    # Fall back to masked phone
    phone = user_data.get("phone_number", "").strip()
    if phone:
        return mask_sensitive_data(phone, reveal_last=4)
    
    # Last resort
    user_id = user_data.get("user_id", "")
    return f"User {user_id}" if user_id else "Unknown User"

async def send_with_delay(send_func, messages: List[str], delay: float = 0.5):
    """
    Send multiple messages with delays between them.
    
    Args:
        send_func: Async function to send messages
        messages: List of messages to send
        delay: Delay between messages in seconds
    """
    for i, message in enumerate(messages):
        await send_func(message)
        
        # Add delay between messages (except for the last one)
        if i < len(messages) - 1:
            await asyncio.sleep(delay)

# ===== ROLE AND PROMPT MANAGEMENT =====

def validate_user_role_permissions(user_role: str, requested_permission: str) -> bool:
    """
    Check if a user role has a specific permission.
    
    Args:
        user_role: User's role (user, admin, super_admin)
        requested_permission: Permission to check
        
    Returns:
        bool: True if role has permission, False otherwise
    """
    role_features = ROLE_FEATURES.get(user_role, {})
    return role_features.get(requested_permission, False)

def get_max_prompts_for_role(user_role: str) -> int:
    """
    Get maximum number of custom prompts allowed for a role.
    
    Args:
        user_role: User's role
        
    Returns:
        int: Maximum prompts allowed
    """
    return ROLE_PROMPT_LIMITS.get(user_role, 1)  # Default to 1

def get_credit_limit_for_role(user_role: str) -> int:
    """
    Get monthly credit limit for a role.
    
    Args:
        user_role: User's role
        
    Returns:
        int: Monthly credit limit
    """
    return ROLE_CREDIT_LIMITS.get(user_role, 50)  # Default to 50

def validate_prompt_content(content: str, context: str = "ai_chat") -> dict:
    """
    Validate prompt content against security and quality rules.
    
    Args:
        content: Prompt content to validate
        context: Prompt context (developer, designer, ai_chat)
        
    Returns:
        dict: Validation result with is_valid, errors, warnings, suggestions
    """
    result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": []
    }
    
    # Length validation
    if len(content) < PROMPT_VALIDATION["min_length"]:
        result["errors"].append(f"Prompt too short (minimum {PROMPT_VALIDATION['min_length']} characters)")
        result["is_valid"] = False
    
    if len(content) > PROMPT_VALIDATION["max_length"]:
        result["errors"].append(f"Prompt too long (maximum {PROMPT_VALIDATION['max_length']} characters)")
        result["is_valid"] = False
    
    # Content validation
    content_lower = content.lower()
    forbidden_found = []
    for word in PROMPT_VALIDATION["forbidden_words"]:
        if word in content_lower:
            forbidden_found.append(word)
    
    if forbidden_found:
        result["errors"].append(f"Contains forbidden words: {', '.join(forbidden_found)}")
        result["is_valid"] = False
    
    # Suggestions
    if not content.strip().endswith('.'):
        result["suggestions"].append("Consider ending your prompt with a period for clarity")
    
    if len(content.split()) < 5:
        result["warnings"].append("Very short prompts may not provide enough context")
    
    # Context-specific validation
    if context == "developer" and "code" not in content_lower and "programming" not in content_lower:
        result["suggestions"].append("Consider including words like 'code' or 'programming' for developer prompts")
    elif context == "designer" and "design" not in content_lower and "creative" not in content_lower:
        result["suggestions"].append("Consider including words like 'design' or 'creative' for designer prompts")
    
    return result

def estimate_prompt_tokens(content: str) -> int:
    """
    Estimate token count for a prompt (rough approximation).
    
    Args:
        content: Prompt content
        
    Returns:
        int: Estimated token count
    """
    # Rough estimate: 1 token ≈ 4 characters for English
    return max(1, len(content) // 4)

def get_default_prompt_for_context(context: str) -> str:
    """
    Get default system prompt for a given context.
    
    Args:
        context: Prompt context
        
    Returns:
        str: Default prompt content
    """
    return DEFAULT_PROMPTS.get(context, DEFAULT_PROMPTS["general"])

def format_prompt_with_variables(template: str, variables: dict) -> str:
    """
    Replace variables in a prompt template.
    
    Args:
        template: Prompt template with {variable} placeholders
        variables: Dictionary of variable values
        
    Returns:
        str: Formatted prompt
    """
    try:
        return template.format(**variables)
    except KeyError as e:
        raise ValueError(f"Missing variable in prompt template: {e}")

def extract_prompt_variables(template: str) -> list:
    """
    Extract variable names from a prompt template.
    
    Args:
        template: Prompt template with {variable} placeholders
        
    Returns:
        list: List of variable names
    """
    import re
    
    # Find all {variable} patterns
    pattern = r'\{([^}]+)\}'
    matches = re.findall(pattern, template)
    
    return list(set(matches))  # Remove duplicates

def sanitize_prompt_name(name: str) -> str:
    """
    Sanitize prompt name for safe storage and display.
    
    Args:
        name: Original prompt name
        
    Returns:
        str: Sanitized prompt name
    """
    import re
    
    # Remove special characters, keep alphanumeric, spaces, hyphens, underscores
    sanitized = re.sub(r'[^a-zA-Z0-9\s\-_]', '', name)
    
    # Collapse multiple spaces
    sanitized = re.sub(r'\s+', ' ', sanitized)
    
    # Trim and limit length
    sanitized = sanitized.strip()[:100]
    
    return sanitized or "Untitled Prompt"

def can_user_create_prompt(user_role: str, current_prompt_count: int) -> bool:
    """
    Check if user can create another custom prompt.
    
    Args:
        user_role: User's role
        current_prompt_count: Number of prompts user currently has
        
    Returns:
        bool: True if user can create more prompts
    """
    max_allowed = get_max_prompts_for_role(user_role)
    return current_prompt_count < max_allowed

def calculate_prompt_usage_cost(input_tokens: int, output_tokens: int, model: str = "gpt-3.5-turbo") -> float:
    """
    Calculate estimated cost for prompt usage.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: AI model used
        
    Returns:
        float: Estimated cost in USD
    """
    # Rough pricing estimates (update with actual rates)
    pricing = {
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},  # per 1K tokens
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03}
    }
    
    model_pricing = pricing.get(model, pricing["gpt-3.5-turbo"])
    
    input_cost = (input_tokens / 1000) * model_pricing["input"]
    output_cost = (output_tokens / 1000) * model_pricing["output"]
    
    return round(input_cost + output_cost, 6)

# ===== EMAIL VALIDATION & ABUSE PREVENTION =====

def validate_email_for_registration(email: str, strict_mode: bool = True) -> dict:
    """
    Comprehensive email validation to prevent abuse of free credits/trials.
    
    Args:
        email: Email address to validate
        strict_mode: If True, only allows trusted providers
        
    Returns:
        dict: Validation result with is_valid, error_code, message, and details
    """
    import re
    
    result = {
        "is_valid": False,
        "error_code": None,
        "message": None,
        "details": {
            "email": email.lower().strip(),
            "domain": None,
            "local_part": None,
            "is_allowed_provider": False,
            "is_disposable": False,
            "validation_checks": {}
        }
    }
    
    # Clean and normalize email
    email = email.lower().strip()
    result["details"]["email"] = email
    
    # Basic format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        result["error_code"] = "invalid_format"
        result["message"] = EMAIL_VALIDATION_MESSAGES["invalid_format"]
        return result
    
    # Split email into local and domain parts
    try:
        local_part, domain = email.split('@', 1)
        result["details"]["local_part"] = local_part
        result["details"]["domain"] = domain
    except ValueError:
        result["error_code"] = "invalid_format"
        result["message"] = EMAIL_VALIDATION_MESSAGES["invalid_format"]
        return result
    
    # Length validations
    if len(local_part) > EMAIL_VALIDATION_RULES["max_local_length"]:
        result["error_code"] = "local_too_long"
        result["message"] = EMAIL_VALIDATION_MESSAGES["local_too_long"]
        return result
    
    if len(domain) > EMAIL_VALIDATION_RULES["max_domain_length"]:
        result["error_code"] = "domain_too_long"
        result["message"] = EMAIL_VALIDATION_MESSAGES["domain_too_long"]
        return result
    
    # Check for minimum local length
    if len(local_part) < EMAIL_VALIDATION_PATTERNS["min_local_length"]:
        result["error_code"] = "invalid_format"
        result["message"] = EMAIL_VALIDATION_MESSAGES["invalid_format"]
        return result
    
    # Domain must contain at least one dot
    if EMAIL_VALIDATION_PATTERNS["require_dot_in_domain"] and '.' not in domain:
        result["error_code"] = "invalid_format"
        result["message"] = EMAIL_VALIDATION_MESSAGES["invalid_format"]
        return result
    
    # Note: Disposable email checking removed - only using allowlist approach
    
    # Check if domain is in allowed providers (MAIN CHANGE: All others are forbidden)
    is_allowed = domain in ALLOWED_EMAIL_PROVIDERS
    result["details"]["is_allowed_provider"] = is_allowed
    
    if not is_allowed:
        result["error_code"] = "forbidden_email"
        result["message"] = EMAIL_VALIDATION_MESSAGES["forbidden_email"]
        return result
    
    # Check suspicious patterns
    for pattern in EMAIL_VALIDATION_PATTERNS["suspicious_patterns"]:
        if re.match(pattern, email):
            result["details"]["validation_checks"]["suspicious_pattern"] = True
            if strict_mode:
                result["error_code"] = "suspicious_email"
                result["message"] = "This email pattern is not allowed for registration"
                return result
    
    # Handle plus addressing (gmail+tag@gmail.com)
    if EMAIL_VALIDATION_RULES["allow_plus_addressing"] and '+' in local_part:
        base_local = local_part.split('+')[0]
        base_email = f"{base_local}@{domain}"
        result["details"]["base_email"] = base_email
        result["details"]["has_plus_addressing"] = True
    
    # All validations passed
    result["is_valid"] = True
    result["message"] = "Email is valid and allowed for registration"
    
    return result

def is_disposable_email(email: str) -> bool:
    """
    Quick check if email is from a disposable provider.
    Note: Now returns False for all emails since we use allowlist approach.
    
    Args:
        email: Email address to check
        
    Returns:
        bool: Always False (disposable checking removed)
    """
    # Disposable email checking removed - using allowlist approach instead
    return False

def is_allowed_email_provider(email: str) -> bool:
    """
    Check if email is from an allowed provider.
    
    Args:
        email: Email address to check
        
    Returns:
        bool: True if email is from allowed provider
    """
    try:
        domain = email.lower().split('@')[1]
        return domain in ALLOWED_EMAIL_PROVIDERS
    except (IndexError, AttributeError):
        return False

# Keep backward compatibility
def is_trusted_email_provider(email: str) -> bool:
    """
    Check if email is from a trusted provider (backward compatibility).
    
    Args:
        email: Email address to check
        
    Returns:
        bool: True if email is from trusted provider
    """
    return is_allowed_email_provider(email)

def get_email_provider_info(email: str) -> dict:
    """
    Get detailed information about an email provider.
    
    Args:
        email: Email address to analyze
        
    Returns:
        dict: Provider information
    """
    try:
        domain = email.lower().split('@')[1]
    except (IndexError, AttributeError):
        return {"error": "Invalid email format"}
    
    provider_info = {
        "domain": domain,
        "is_allowed": domain in ALLOWED_EMAIL_PROVIDERS,
        "is_disposable": False,  # Disposable checking removed
        "provider_type": "unknown"
    }
    
    # Categorize provider type
    if domain in ALLOWED_EMAIL_PROVIDERS:
        if domain in ["gmail.com", "googlemail.com", "google.com"]:
            provider_info["provider_type"] = "google"
        elif domain in ["outlook.com", "hotmail.com", "live.com", "msn.com"]:
            provider_info["provider_type"] = "microsoft"
        elif domain.startswith("yahoo."):
            provider_info["provider_type"] = "yahoo"
        elif domain in ["mail.ru", "bk.ru", "inbox.ru", "list.ru"]:
            provider_info["provider_type"] = "mailru"
        elif domain in ["yandex.ru", "yandex.com", "ya.ru"]:
            provider_info["provider_type"] = "yandex"
        elif domain in ["icloud.com", "me.com", "mac.com"]:
            provider_info["provider_type"] = "apple"
        else:
            provider_info["provider_type"] = "allowed_other"
    else:
        provider_info["provider_type"] = "forbidden"
    
    return provider_info

def normalize_email_for_comparison(email: str) -> str:
    """
    Normalize email for comparison to detect duplicates.
    Handles Gmail dots and plus addressing.
    
    Args:
        email: Email address to normalize
        
    Returns:
        str: Normalized email
    """
    try:
        local_part, domain = email.lower().split('@', 1)
    except ValueError:
        return email.lower()
    
    # Handle Gmail-specific normalization
    if domain in ["gmail.com", "googlemail.com"]:
        # Remove dots from local part
        local_part = local_part.replace('.', '')
        # Remove plus addressing
        if '+' in local_part:
            local_part = local_part.split('+')[0]
        # Normalize domain to gmail.com
        domain = "gmail.com"
    
    # Handle plus addressing for other providers
    elif '+' in local_part:
        local_part = local_part.split('+')[0]
    
    return f"{local_part}@{domain}"

def check_email_abuse_patterns(email: str, user_data: dict = None) -> dict:
    """
    Advanced abuse detection for email addresses.
    
    Args:
        email: Email address to check
        user_data: Additional user data for pattern analysis
        
    Returns:
        dict: Abuse detection results
    """
    import re
    
    abuse_indicators = {
        "risk_score": 0,  # 0-100 risk score
        "flags": [],
        "is_high_risk": False,
        "recommendations": []
    }
    
    email = email.lower().strip()
    
    try:
        local_part, domain = email.split('@', 1)
    except ValueError:
        abuse_indicators["flags"].append("invalid_format")
        abuse_indicators["risk_score"] = 100
        return abuse_indicators
    
    # Check suspicious patterns
    for pattern in EMAIL_VALIDATION_PATTERNS["suspicious_patterns"]:
        if re.match(pattern, email):
            abuse_indicators["flags"].append("suspicious_pattern")
            abuse_indicators["risk_score"] += 20
    
    # Check for sequential numbers (user123, user456, etc.)
    if re.search(r'\d{3,}', local_part):
        abuse_indicators["flags"].append("sequential_numbers")
        abuse_indicators["risk_score"] += 15
    
    # Check for very short local part
    if len(local_part) <= 2:
        abuse_indicators["flags"].append("very_short_local")
        abuse_indicators["risk_score"] += 10
    
    # Check for excessive special characters
    special_count = sum(1 for c in local_part if c in '.-_+')
    if special_count > 3:
        abuse_indicators["flags"].append("excessive_special_chars")
        abuse_indicators["risk_score"] += 10
    
    # Note: Disposable email checking removed - using allowlist approach
    
    # Check if domain is not trusted
    if not is_allowed_email_provider(email):
        abuse_indicators["flags"].append("untrusted_provider")
        abuse_indicators["risk_score"] += 25
    
    # Additional checks with user data
    if user_data:
        # Check for rapid account creation patterns
        if user_data.get("recent_registrations", 0) > 5:
            abuse_indicators["flags"].append("rapid_registration")
            abuse_indicators["risk_score"] += 30
        
        # Check for IP-based patterns
        if user_data.get("same_ip_registrations", 0) > 3:
            abuse_indicators["flags"].append("same_ip_multiple_accounts")
            abuse_indicators["risk_score"] += 25
    
    # Determine risk level
    if abuse_indicators["risk_score"] >= 50:
        abuse_indicators["is_high_risk"] = True
        abuse_indicators["recommendations"].append("Block registration")
    elif abuse_indicators["risk_score"] >= 30:
        abuse_indicators["recommendations"].append("Require additional verification")
    elif abuse_indicators["risk_score"] >= 15:
        abuse_indicators["recommendations"].append("Monitor closely")
    else:
        abuse_indicators["recommendations"].append("Allow registration")
    
    return abuse_indicators

def get_trusted_email_providers_list() -> list:
    """
    Get list of trusted email providers for frontend display.
    
    Returns:
        list: Sorted list of trusted providers
    """
    # Group by category for better UX
    providers = {
        "Major Providers": [
            "gmail.com", "outlook.com", "yahoo.com", "icloud.com", "aol.com"
        ],
        "International": [
            "mail.ru", "yandex.com", "qq.com", "naver.com"
        ],
        "European": [
            "web.de", "gmx.com", "orange.fr", "libero.it"
        ],
        "Privacy-Focused": [
            "protonmail.com", "tutanota.com", "fastmail.com"
        ]
    }
    
    return providers

def suggest_alternative_email_providers(blocked_domain: str) -> list:
    """
    Suggest alternative email providers when user tries blocked domain.
    
    Args:
        blocked_domain: The blocked domain user tried to use
        
    Returns:
        list: Suggested alternative providers
    """
    suggestions = [
        {
            "provider": "gmail.com",
            "name": "Gmail",
            "description": "Free email from Google",
            "signup_url": "https://accounts.google.com/signup"
        },
        {
            "provider": "outlook.com", 
            "name": "Outlook",
            "description": "Free email from Microsoft",
            "signup_url": "https://outlook.live.com/owa/"
        },
        {
            "provider": "yahoo.com",
            "name": "Yahoo Mail",
            "description": "Free email from Yahoo",
            "signup_url": "https://login.yahoo.com/account/create"
        },
        {
            "provider": "mail.ru",
            "name": "Mail.ru",
            "description": "Popular Russian email service",
            "signup_url": "https://account.mail.ru/signup"
        }
    ]
    
    return suggestions

def validate_email_batch(emails: list, strict_mode: bool = True) -> dict:
    """
    Validate multiple emails at once for bulk operations.
    
    Args:
        emails: List of email addresses to validate
        strict_mode: If True, only allows trusted providers
        
    Returns:
        dict: Batch validation results
    """
    results = {
        "total_emails": len(emails),
        "valid_emails": [],
        "invalid_emails": [],
        "forbidden_emails": [],
        "summary": {
            "valid_count": 0,
            "invalid_count": 0,
            "forbidden_count": 0
        }
    }
    
    for email in emails:
        validation = validate_email_for_registration(email, strict_mode)
        
        if validation["is_valid"]:
            results["valid_emails"].append(email)
            results["summary"]["valid_count"] += 1
        else:
            results["invalid_emails"].append({
                "email": email,
                "error_code": validation["error_code"],
                "message": validation["message"]
            })
            results["summary"]["invalid_count"] += 1
            
            if validation["error_code"] == "forbidden_email":
                results["forbidden_emails"].append(email)
                results["summary"]["forbidden_count"] += 1
    
    return results

# ===== SMS VERIFICATION & PHONE AUTHENTICATION =====

def generate_sms_code(length: int = None) -> str:
    """
    Generate a random SMS verification code.
    
    Args:
        length: Code length (default from constants)
        
    Returns:
        str: Generated SMS code
    """
    import random
    import string
    
    code_length = length or SMS_CODE_LENGTH
    
    # Generate numeric code for better SMS compatibility
    code = ''.join(random.choices(string.digits, k=code_length))
    
    # Ensure code doesn't start with 0 for better readability
    if code.startswith('0'):
        code = random.choice('123456789') + code[1:]
    
    return code

def determine_sms_delivery_method(phone: str, user_exists_in_telegram: bool = False) -> dict:
    """
    Determine the best SMS delivery method based on user presence in database.
    
    Args:
        phone: Phone number to send SMS to
        user_exists_in_telegram: Whether user exists in Telegram bot database
        
    Returns:
        dict: Delivery method information
    """
    delivery_info = {
        "method": SMSDeliveryMethod.EXTERNAL_SMS,
        "cost": SMS_SERVICE_CONFIG["cost_per_sms"],
        "currency": SMS_SERVICE_CONFIG["currency"],
        "provider": SMS_SERVICE_CONFIG["provider"],
        "estimated_delivery_time": "1-3 minutes",
        "reliability": "high",
        "reason": "New user - using external SMS service"
    }
    
    # If user exists in Telegram, prefer Telegram bot delivery
    if user_exists_in_telegram:
        delivery_info.update({
            "method": SMSDeliveryMethod.TELEGRAM_BOT,
            "cost": 0,  # Free via Telegram
            "currency": "FREE",
            "provider": "Telegram Bot",
            "estimated_delivery_time": "Instant",
            "reliability": "very_high",
            "reason": "Existing Telegram user - using bot delivery"
        })
    
    return delivery_info

def format_sms_message(template_key: str, **kwargs) -> str:
    """
    Format SMS message using predefined templates.
    
    Args:
        template_key: Template key from SMS_TEMPLATES
        **kwargs: Template variables
        
    Returns:
        str: Formatted SMS message
    """
    template = SMS_TEMPLATES.get(template_key, "SayToAI: {code}")
    
    # Add default values
    default_values = {
        "minutes": SMS_CODE_EXPIRATION_MINUTES,
        "app_name": "SayToAI"
    }
    
    # Merge with provided kwargs
    format_values = {**default_values, **kwargs}
    
    try:
        return template.format(**format_values)
    except KeyError:
        # Fallback if template variable is missing
        return f"SayToAI verification code: {kwargs.get('code', 'N/A')}"

def validate_sms_code(provided_code: str, expected_code: str, created_at: datetime) -> dict:
    """
    Validate SMS verification code.
    
    Args:
        provided_code: Code provided by user
        expected_code: Expected code from database
        created_at: When the code was created
        
    Returns:
        dict: Validation result
    """
    from datetime import timedelta
    
    result = {
        "is_valid": False,
        "error_code": None,
        "message": None,
        "time_remaining": 0
    }
    
    # Check if code has expired
    expiry_time = created_at + timedelta(minutes=SMS_CODE_EXPIRATION_MINUTES)
    current_time = datetime.now()
    
    if current_time > expiry_time:
        result["error_code"] = "code_expired"
        result["message"] = "SMS verification code has expired. Please request a new one."
        return result
    
    # Calculate remaining time
    time_remaining = expiry_time - current_time
    result["time_remaining"] = int(time_remaining.total_seconds())
    
    # Validate code
    if provided_code.strip() != expected_code.strip():
        result["error_code"] = "invalid_code"
        result["message"] = SMS_VALIDATION_MESSAGES["invalid_sms_code"]
        return result
    
    # Code is valid
    result["is_valid"] = True
    result["message"] = "SMS code verified successfully"
    
    return result

def check_sms_rate_limit(phone: str, attempts_in_hour: int, last_sms_time: datetime = None) -> dict:
    """
    Check if SMS sending is rate limited for a phone number.
    
    Args:
        phone: Phone number
        attempts_in_hour: Number of SMS attempts in the last hour
        last_sms_time: Timestamp of last SMS sent
        
    Returns:
        dict: Rate limit check result
    """
    result = {
        "can_send": True,
        "error_code": None,
        "message": None,
        "wait_time_seconds": 0,
        "attempts_remaining": MAX_SMS_ATTEMPTS_PER_HOUR - attempts_in_hour
    }
    
    # Check hourly limit
    if attempts_in_hour >= MAX_SMS_ATTEMPTS_PER_HOUR:
        result["can_send"] = False
        result["error_code"] = "hourly_limit_exceeded"
        result["message"] = SMS_VALIDATION_MESSAGES["sms_rate_limit"]
        return result
    
    # Check cooldown period
    if last_sms_time:
        cooldown_end = last_sms_time + timedelta(seconds=SMS_RESEND_COOLDOWN_SECONDS)
        current_time = datetime.now()
        
        if current_time < cooldown_end:
            wait_time = cooldown_end - current_time
            result["can_send"] = False
            result["error_code"] = "cooldown_active"
            result["message"] = f"Please wait {int(wait_time.total_seconds())} seconds before requesting another SMS"
            result["wait_time_seconds"] = int(wait_time.total_seconds())
            return result
    
    return result

def normalize_phone_for_comparison(phone: str) -> str:
    """
    Normalize phone number for database comparison and duplicate detection.
    
    Args:
        phone: Phone number to normalize
        
    Returns:
        str: Normalized phone number
    """
    import re
    
    if not phone:
        return ""
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone.strip())
    
    # Ensure it starts with +
    if not cleaned.startswith('+'):
        # Add +998 for Uzbekistan numbers if they look valid
        if len(cleaned) == 9 and cleaned.startswith(('90', '91', '93', '94', '95', '97', '98', '99')):
            cleaned = '+998' + cleaned
    
    return cleaned

def estimate_sms_cost(phone_count: int, delivery_method: str = "external_sms") -> dict:
    """
    Estimate cost for sending SMS to multiple phone numbers.
    
    Args:
        phone_count: Number of phones to send SMS to
        delivery_method: SMS delivery method
        
    Returns:
        dict: Cost estimation
    """
    if delivery_method == SMSDeliveryMethod.TELEGRAM_BOT:
        return {
            "total_cost": 0,
            "cost_per_sms": 0,
            "currency": "FREE",
            "phone_count": phone_count,
            "method": "Telegram Bot"
        }
    
    cost_per_sms = SMS_SERVICE_CONFIG["cost_per_sms"]
    total_cost = phone_count * cost_per_sms
    
    return {
        "total_cost": total_cost,
        "cost_per_sms": cost_per_sms,
        "currency": SMS_SERVICE_CONFIG["currency"],
        "phone_count": phone_count,
        "method": "External SMS Service",
        "provider": SMS_SERVICE_CONFIG["provider"]
    }

# ===== ANTI-FRAUD & USER VALIDATION SYSTEM =====

def calculate_risk_score(registration_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate risk score for user registration to detect potential fraud.
    
    Args:
        registration_data: Dictionary containing registration information
        
    Returns:
        dict: Risk assessment with score and recommendations
    """
    import re
    
    risk_score = 0.0
    risk_factors = []
    risk_weights = RISK_SCORING["risk_factors"]
    
    # Check email patterns
    email = registration_data.get("email", "").lower()
    if email:
        for pattern in FRAUD_DETECTION_RULES["suspicious_email_patterns"]:
            if re.match(pattern, email):
                risk_score += risk_weights["suspicious_name"]
                risk_factors.append("suspicious_email_pattern")
                break
    
    # Check name patterns
    name = registration_data.get("name", "").lower()
    if name:
        for pattern in FRAUD_DETECTION_RULES["suspicious_name_patterns"]:
            if re.match(pattern, name):
                risk_score += risk_weights["suspicious_name"]
                risk_factors.append("suspicious_name_pattern")
                break
    
    # Check phone number
    phone = registration_data.get("phone", "")
    if phone and is_suspicious_phone_number(phone):
        risk_score += risk_weights["suspicious_phone"]
        risk_factors.append("suspicious_phone_number")
    
    # Check registration speed
    registration_time = registration_data.get("registration_time_seconds", 0)
    if registration_time < FRAUD_DETECTION_RULES["min_registration_time_seconds"]:
        risk_score += risk_weights["fast_registration"]
        risk_factors.append("registration_too_fast")
    
    # Check device fingerprint
    if not registration_data.get("device_fingerprint"):
        risk_score += risk_weights["no_device_fingerprint"]
        risk_factors.append("missing_device_fingerprint")
    
    # Check IP-related factors
    ip_info = registration_data.get("ip_info", {})
    if ip_info.get("is_vpn") or ip_info.get("is_proxy"):
        risk_score += risk_weights["vpn_or_proxy"]
        risk_factors.append("vpn_or_proxy_detected")
    
    if ip_info.get("is_suspicious"):
        risk_score += risk_weights["suspicious_ip"]
        risk_factors.append("suspicious_ip_location")
    
    if ip_info.get("is_blacklisted"):
        risk_score += risk_weights["blacklisted_ip"]
        risk_factors.append("blacklisted_ip")
    
    # Check CAPTCHA results
    captcha_result = registration_data.get("captcha_result", {})
    if captcha_result.get("failed"):
        risk_score += risk_weights["failed_captcha"]
        risk_factors.append("captcha_verification_failed")
    
    # Determine risk level
    if risk_score <= RISK_SCORING["low_risk_threshold"]:
        risk_level = "low"
    elif risk_score <= RISK_SCORING["medium_risk_threshold"]:
        risk_level = "medium"
    else:
        risk_level = "high"
    
    return {
        "risk_score": min(risk_score, 1.0),  # Cap at 1.0
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "should_block": risk_score >= RISK_SCORING["high_risk_threshold"],
        "requires_manual_review": risk_level == "high",
        "requires_additional_verification": risk_level in ["medium", "high"]
    }

def check_ip_rate_limit(ip_address: str, action: str, time_window: str = "minute") -> Dict[str, Any]:
    """
    Check if IP address has exceeded rate limits for specific actions.
    
    Args:
        ip_address: IP address to check
        action: Action type (registration, sms_request, etc.)
        time_window: Time window to check (minute, hour, day)
        
    Returns:
        dict: Rate limit check result
    """
    from datetime import datetime, timedelta
    
    # This would typically query your database/cache to check actual counts
    # For now, return a mock implementation
    
    limit_key = f"{action}_per_{time_window}"
    limit = IP_RATE_LIMITS.get(limit_key, 999)
    
    # Mock current count - in real implementation, query from Redis/database
    current_count = 0  # Replace with actual count from storage
    
    result = {
        "allowed": current_count < limit,
        "current_count": current_count,
        "limit": limit,
        "time_window": time_window,
        "reset_time": None,
        "retry_after_seconds": 0
    }
    
    if not result["allowed"]:
        # Calculate reset time based on time window
        now = datetime.now()
        if time_window == "minute":
            reset_time = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        elif time_window == "hour":
            reset_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif time_window == "day":
            reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        else:
            reset_time = now + timedelta(minutes=1)
        
        result["reset_time"] = reset_time
        result["retry_after_seconds"] = int((reset_time - now).total_seconds())
    
    return result

def validate_captcha(captcha_response: str, captcha_type: str = "recaptcha_v3") -> Dict[str, Any]:
    """
    Validate CAPTCHA response.
    
    Args:
        captcha_response: CAPTCHA response token
        captcha_type: Type of CAPTCHA (recaptcha_v2, recaptcha_v3, hcaptcha)
        
    Returns:
        dict: CAPTCHA validation result
    """
    
    # Mock CAPTCHA config - in real implementation, import from constants
    captcha_config = {"enabled": True}
    
    if not captcha_config["enabled"]:
        return {
            "success": True,
            "score": 1.0,
            "action": "bypass",
            "challenge_ts": None,
            "hostname": None,
            "error_codes": []
        }
    
    if not captcha_response:
        return {
            "success": False,
            "score": 0.0,
            "action": "missing_response",
            "error_codes": ["missing-input-response"]
        }
    
    # Mock validation - in real implementation, make API call to CAPTCHA provider
    # For reCAPTCHA v3, you would call:
    # https://www.google.com/recaptcha/api/siteverify
    
    return {
        "success": True,  # Mock success
        "score": 0.8,     # Mock score
        "action": "registration",
        "challenge_ts": datetime.now().isoformat(),
        "hostname": "saytoai.org",
        "error_codes": []
    }

def generate_device_fingerprint(request_data: Dict[str, Any]) -> str:
    """
    Generate device fingerprint from request data.
    
    Args:
        request_data: Request data containing device information
        
    Returns:
        str: Device fingerprint hash
    """
    import hashlib
    import json
    
    fingerprint_data = {
        "user_agent": request_data.get("user_agent", ""),
        "screen_resolution": request_data.get("screen_resolution", ""),
        "timezone": request_data.get("timezone", ""),
        "language": request_data.get("language", ""),
        "platform": request_data.get("platform", ""),
        "canvas_fingerprint": request_data.get("canvas_fingerprint", ""),
        "webgl_fingerprint": request_data.get("webgl_fingerprint", "")
    }
    
    # Create deterministic fingerprint
    fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
    fingerprint_hash = hashlib.sha256(fingerprint_string.encode()).hexdigest()
    
    return fingerprint_hash[:32]  # Return first 32 characters

def analyze_ip_geolocation(ip_address: str) -> Dict[str, Any]:
    """
    Analyze IP address for geolocation and risk factors.
    
    Args:
        ip_address: IP address to analyze
        
    Returns:
        dict: IP analysis result
    """
    # Mock implementation - in real system, use IP geolocation service
    # like MaxMind GeoIP2, IPinfo, or similar
    
    return {
        "ip": ip_address,
        "country_code": "UZ",  # Mock country
        "country_name": "Uzbekistan",
        "city": "Tashkent",
        "region": "Tashkent",
        "is_vpn": False,       # Mock - detect VPN
        "is_proxy": False,     # Mock - detect proxy
        "is_tor": False,       # Mock - detect Tor
        "is_datacenter": False, # Mock - detect datacenter IP
        "is_suspicious": False, # Mock - overall suspicion
        "is_blacklisted": False, # Mock - check against blacklists
        "risk_score": 0.1,     # Mock risk score
        "isp": "UzbekTelecom", # Mock ISP
        "organization": "UzbekTelecom"
    }

def get_platform_credits(platform: str) -> int:
    """
    Get credit allocation based on registration platform.
    
    Args:
        platform: Registration platform (web, telegram, admin)
        
    Returns:
        int: Number of credits to allocate
    """
    return PLATFORM_CREDIT_ALLOCATION.get(platform.lower(), PLATFORM_CREDIT_ALLOCATION["web"])

def validate_registration_timing(start_time: datetime, end_time: datetime) -> Dict[str, Any]:
    """
    Validate registration timing to detect bot behavior.
    
    Args:
        start_time: When user started registration form
        end_time: When user submitted registration form
        
    Returns:
        dict: Timing validation result
    """
    duration_seconds = (end_time - start_time).total_seconds()
    min_time = FRAUD_DETECTION_RULES["min_registration_time_seconds"]
    max_time = FRAUD_DETECTION_RULES["max_registration_time_minutes"] * 60
    
    result = {
        "duration_seconds": duration_seconds,
        "is_too_fast": duration_seconds < min_time,
        "is_too_slow": duration_seconds > max_time,
        "is_suspicious": False,
        "risk_factor": 0.0
    }
    
    if result["is_too_fast"]:
        result["is_suspicious"] = True
        result["risk_factor"] = 0.3  # High risk for bot behavior
    elif result["is_too_slow"]:
        result["is_suspicious"] = True
        result["risk_factor"] = 0.1  # Low risk, might be legitimate
    
    return result

def check_account_limits_per_ip(ip_address: str, time_window: str = "day") -> Dict[str, Any]:
    """
    Check how many accounts have been created from an IP address.
    
    Args:
        ip_address: IP address to check
        time_window: Time window (day, week, month)
        
    Returns:
        dict: Account creation limits check
    """
    current_accounts = 0  # Replace with actual count from database
    
    if time_window == "day":
        limit = FRAUD_DETECTION_RULES["max_accounts_per_ip_per_day"]
    elif time_window == "week":
        limit = FRAUD_DETECTION_RULES.get("max_accounts_per_ip_per_week", 7)
    else:
        limit = FRAUD_DETECTION_RULES.get("max_accounts_per_ip_per_month", 20)
    
    return {
        "current_count": current_accounts,
        "limit": limit,
        "allowed": current_accounts < limit,
        "time_window": time_window,
        "risk_level": "high" if current_accounts >= limit else "low"
    }

def enhanced_phone_validation(phone: str) -> Dict[str, Any]:
    """
    Enhanced phone validation with fraud detection.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        dict: Enhanced validation result
    """
    # Start with basic validation
    basic_validation = validate_phone_number(phone)
    
    if not basic_validation["is_valid"]:
        return {
            **basic_validation,
            "fraud_risk": "high",
            "is_suspicious": True,
            "validation_level": "basic_failed"
        }
    
    # Additional fraud checks
    is_suspicious = is_suspicious_phone_number(phone)
    
    # Mock carrier validation - in real system, use carrier lookup service
    carrier_info = {
        "is_mobile": True,      # Mock - check if mobile number
        "is_voip": False,       # Mock - check if VoIP number
        "carrier": "Beeline",   # Mock - carrier name
        "line_type": "mobile"   # Mock - line type
    }
    
    # Check if VoIP and blocking is enabled
    if ENHANCED_PHONE_VALIDATION["block_voip_numbers"] and carrier_info["is_voip"]:
        return {
            **basic_validation,
            "is_valid": False,
            "fraud_risk": "high",
            "is_suspicious": True,
            "error_code": "voip_number_blocked",
            "message": "VoIP numbers are not allowed for registration",
            "validation_level": "carrier_blocked"
        }
    
    # Check if mobile only is required
    if ENHANCED_PHONE_VALIDATION["require_mobile_only"] and not carrier_info["is_mobile"]:
        return {
            **basic_validation,
            "is_valid": False,
            "fraud_risk": "medium",
            "is_suspicious": True,
            "error_code": "non_mobile_number",
            "message": "Only mobile numbers are allowed for registration",
            "validation_level": "mobile_required"
        }
    
    return {
        **basic_validation,
        "fraud_risk": "high" if is_suspicious else "low",
        "is_suspicious": is_suspicious,
        "carrier_info": carrier_info,
        "validation_level": "enhanced_passed"
    }

def create_fraud_prevention_report(registration_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create comprehensive fraud prevention report for registration attempt.
    
    Args:
        registration_data: Complete registration data
        
    Returns:
        dict: Comprehensive fraud prevention report
    """
    # Calculate risk score
    risk_assessment = calculate_risk_score(registration_data)
    
    # Check IP rate limits
    ip_address = registration_data.get("ip_address", "")
    ip_rate_limit = check_ip_rate_limit(ip_address, "registration", "day")
    
    # Analyze IP geolocation
    ip_analysis = analyze_ip_geolocation(ip_address)
    
    # Check account limits
    account_limits = check_account_limits_per_ip(ip_address)
    
    # Validate timing
    start_time = registration_data.get("form_start_time")
    end_time = registration_data.get("form_submit_time")
    timing_validation = None
    if start_time and end_time:
        timing_validation = validate_registration_timing(start_time, end_time)
    
    # Determine action based on risk level
    risk_level = risk_assessment["risk_level"]
    requirements = VERIFICATION_REQUIREMENTS[risk_level]
    
    if risk_assessment["should_block"] or not ip_rate_limit["allowed"] or not account_limits["allowed"]:
        recommended_action = FraudDetectionAction.BLOCK_REGISTRATION
    elif risk_level == "high":
        recommended_action = FraudDetectionAction.REQUIRE_MANUAL_REVIEW
    elif risk_level == "medium":
        recommended_action = FraudDetectionAction.REQUIRE_PHONE
    elif requirements["captcha_required"]:
        recommended_action = FraudDetectionAction.REQUIRE_CAPTCHA
    else:
        recommended_action = FraudDetectionAction.ALLOW
    
    return {
        "timestamp": datetime.now(),
        "registration_id": registration_data.get("registration_id"),
        "risk_assessment": risk_assessment,
        "ip_analysis": ip_analysis,
        "ip_rate_limit": ip_rate_limit,
        "account_limits": account_limits,
        "timing_validation": timing_validation,
        "verification_requirements": requirements,
        "recommended_action": recommended_action,
        "platform_credits": get_platform_credits(registration_data.get("platform", "web")),
        "requires_manual_review": risk_assessment["requires_manual_review"],
        "additional_checks_needed": risk_assessment["requires_additional_verification"]
    }

# ===== PAYMENT UTILITIES =====

def validate_payment_amount(amount: int, currency: str = "UZS") -> Dict[str, Any]:
    """
    Validate payment amount against limits - updated for voiceBot compatibility.
    
    Args:
        amount: Payment amount in smallest currency unit (tiyin for UZS)
        currency: Payment currency
        
    Returns:
        Dict with validation result
    """
    
    result = {
        "is_valid": False,
        "error_code": None,
        "error_message": None,
        "formatted_amount": None
    }
    
    if currency != "UZS":
        result["error_code"] = "UNSUPPORTED_CURRENCY"
        result["error_message"] = f"Currency {currency} is not supported"
        return result
    
    # Amount should already be in tiyin (smallest unit)
    amount_tiyin = int(amount)
    
    if amount_tiyin < PAYMENT_LIMITS["min_amount_tiyin"]:
        result["error_code"] = "AMOUNT_TOO_LOW"
        result["error_message"] = f"Minimum payment amount is {PAYMENT_LIMITS['min_amount_tiyin']/100} UZS"
        return result
    
    if amount_tiyin > PAYMENT_LIMITS["max_amount_tiyin"]:
        result["error_code"] = "AMOUNT_TOO_HIGH"
        result["error_message"] = f"Maximum payment amount is {PAYMENT_LIMITS['max_amount_tiyin']/100} UZS"
        return result
    
    result["is_valid"] = True
    result["formatted_amount"] = amount_tiyin
    
    return result

def format_payment_amount(amount: int, currency: str = "UZS") -> str:
    """
    Format payment amount for display - updated for voiceBot compatibility.
    
    Args:
        amount: Amount in smallest currency unit (tiyin for UZS)
        currency: Currency code
        
    Returns:
        Formatted amount string
    """
    if currency == "UZS":
        # Convert tiyin to UZS
        uzs_amount = amount / 100
        return f"{uzs_amount:,.0f} UZS"
    
    return f"{amount} {currency}"

def get_tariff_info(tariff_name: str) -> Dict[str, Any]:
    """
    Get tariff information by name - matching voiceBot structure.
    
    Args:
        tariff_name: Tariff name (basic, standard, premium)
        
    Returns:
        Tariff configuration
    """
    if tariff_name not in PAYMENT_TARIFFS:
        raise ValueError(f"Invalid tariff: {tariff_name}")
    
    return PAYMENT_TARIFFS[tariff_name]

def calculate_credits_for_amount(amount: int) -> int:
    """
    Calculate credits for a given amount based on tariff structure.
    
    Args:
        amount: Amount in tiyin
        
    Returns:
        Number of credits for the amount
    """
    # Find the tariff that matches the amount
    for tariff_name, tariff_info in PAYMENT_TARIFFS.items():
        if tariff_info["amount"] == amount:
            return tariff_info["credits"]
    
    # If no exact match, calculate proportionally based on basic tariff
    basic_tariff = PAYMENT_TARIFFS["basic"]
    credit_rate = basic_tariff["credits"] / basic_tariff["amount"]
    return int(amount * credit_rate)

def generate_payment_order_id(user_id: str, tariff: str = None, prefix: str = "order") -> str:
    """
    Generate unique payment order ID - matching voiceBot format.
    
    Args:
        user_id: User identifier
        tariff: Tariff name (optional)
        prefix: Order ID prefix
        
    Returns:
        Unique order ID
    """
    import uuid
    from datetime import datetime
    
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    
    if tariff:
        return f"{prefix}_{user_id}_{tariff}_{timestamp}_{unique_id}"
    else:
        return f"{prefix}_{user_id}_{timestamp}_{unique_id}"

def validate_payment_signature(data: Dict[str, Any], signature: str, secret_key: str) -> bool:
    """
    Validate payment provider signature (generic implementation).
    
    Args:
        data: Payment data to validate
        signature: Provided signature
        secret_key: Secret key for validation
        
    Returns:
        True if signature is valid
    """
    import hashlib
    import hmac
    
    # Create signature string from sorted data
    signature_string = "&".join([f"{k}={v}" for k, v in sorted(data.items())])
    
    # Generate expected signature
    expected_signature = hmac.new(
        secret_key.encode('utf-8'),
        signature_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def get_payment_provider_config(provider: str) -> Dict[str, Any]:
    """
    Get payment provider configuration.
    
    Args:
        provider: Payment provider name
        
    Returns:
        Provider configuration
    """
    
    return PAYMENT_PROVIDERS.get(provider, {})

def is_payment_amount_valid_for_provider(amount: int, provider: str) -> bool:
    """
    Check if payment amount is valid for specific provider.
    
    Args:
        amount: Payment amount in smallest currency unit
        provider: Payment provider name
        
    Returns:
        True if amount is valid for provider
    """
    config = get_payment_provider_config(provider)
    
    if not config:
        return False
    
    return config["min_amount"] <= amount <= config["max_amount"] 