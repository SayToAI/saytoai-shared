"""
SayToAI Shared Constants and Enums
==================================

Centralized configuration, constants, and enumerations for the entire SayToAI ecosystem.
This module contains all shared constants extracted from the original SayToAI project
and organized for use across all services.

Key Components:
- 🏗️ Service configuration and tiers
- 💳 Payment system constants (voiceBot compatible)
- 📱 SMS and communication settings
- 🔐 Authentication and security rules
- 🛡️ Fraud prevention configurations
- 🌐 Multi-language support
- 📊 Rate limiting and validation rules

Usage:
    from saytoai_shared.constants import (
        SERVICE_TIERS, PaymentStatus, UserRole,
        PAYMENT_TARIFFS, SMS_CONFIGURATION
    )

Version: 0.0.1
Last Updated: 2025-06-15
"""

from enum import Enum
from .prompts import DEVELOPER_PROMPT, DESIGNER_PROMPT, AI_CHAT_PROMPT

# ============================================================================
# CORE SERVICE CONFIGURATION
# ============================================================================

# Service tiers available to users (free → basic → standard → premium)
SERVICE_TIERS = ["free", "basic", "standard", "premium"]

# Default credits awarded to new users upon registration
INITIAL_FREE_CREDITS = 50

# Administrative contact numbers for system management
ADMIN_PHONE = "+998975320398"        # Primary admin contact
SUPER_ADMIN_PHONE = "+998995320398"  # Super admin contact

# ============================================================================
# DEFAULT SYSTEM SETTINGS
# ============================================================================

# Default language settings for new users
DEFAULT_LANGUAGE = "english"          # UI language
DEFAULT_AUDIO_LANGUAGE = "auto"       # Audio processing language (auto-detect)
DEFAULT_OUTPUT_LANGUAGE = "english"   # Output/response language
DEFAULT_ROLE = "user"                 # Default user role

# ============================================================================
# PAYMENT SYSTEM CONFIGURATION
# ============================================================================

# Payment system defaults (voiceBot compatible)
DEFAULT_CURRENCY = "UZS"                           # Uzbekistan Som
SUPPORTED_PAYMENT_METHODS = ["payme", "click"]     # Available payment providers
SUPPORTED_CURRENCIES = ["UZS", "USD"]              # Supported currencies

# Service response constants
HTTP_STATUS_CODES = {
    "OK": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "INTERNAL_SERVER_ERROR": 500,
}

# Custom prompt limits
MAX_CUSTOM_PROMPT_LENGTH = 4000
MAX_CUSTOM_PROMPT_COUNT = 1

# Message and content limits
MAX_AUDIO_DURATION_SECONDS = 3600
MAX_FILE_SIZE_MB = 10

# Authentication constants
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
EMAIL_CODE_LENGTH = 6
EMAIL_CODE_EXPIRATION_MINUTES = 10
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

# Enums - Updated based on new business logic
class SubscriptionType(Enum):
    """User subscription types - updated to match new tiers."""
    FREE_TRIAL = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"

class SubscriptionStatus(Enum):
    """Subscription status values."""
    ACTIVE = "active"
    EXPIRED = "expired" 
    SUSPENDED = "suspended"

class PaymentStatus(Enum):
    """Payment transaction statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class RequestStatus(Enum):
    """Admin request status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class LogLevel(Enum):
    """System log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Platform(Enum):
    """Platform types for service access."""
    TELEGRAM = "telegram"
    WEB = "web"
    API = "api"
    ADMIN = "admin"

class TaskStatus(Enum):
    """Task processing statuses (from worker_manager.py)."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"

class WorkerStatus(Enum):
    """Worker system statuses."""
    IDLE = "idle"
    BUSY = "busy"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"

class UserRole(str, Enum):
    """User roles enum for better type safety."""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class AuthMethod(str, Enum):
    """Authentication method types."""
    EMAIL = "email"
    TELEGRAM = "telegram"
    PHONE = "phone"

class EmailCodePurpose(str, Enum):
    """Email verification code purposes."""
    REGISTRATION = "registration"
    PASSWORD_RESET = "password_reset"

# Mapping dictionaries for easy access
SUBSCRIPTION_TYPES = {
    "free": SubscriptionType.FREE_TRIAL,
    "basic": SubscriptionType.BASIC,
    "standard": SubscriptionType.STANDARD,
    "premium": SubscriptionType.PREMIUM,
}

PAYMENT_STATUSES = {
    "pending": PaymentStatus.PENDING,
    "completed": PaymentStatus.COMPLETED,
    "failed": PaymentStatus.FAILED,
    "refunded": PaymentStatus.REFUNDED,
}

LOG_LEVELS = {
    "debug": LogLevel.DEBUG,
    "info": LogLevel.INFO,
    "warning": LogLevel.WARNING,
    "error": LogLevel.ERROR,
    "critical": LogLevel.CRITICAL,
}

PLATFORMS = {
    "telegram": Platform.TELEGRAM,
    "web": Platform.WEB,
    "api": Platform.API,
    "admin": Platform.ADMIN,
}

USER_ROLES = {
    "user": UserRole.USER,
    "admin": UserRole.ADMIN,
    "super_admin": UserRole.SUPER_ADMIN,
}

# Language and localization constants - simplified based on actual support
SUPPORTED_LANGUAGES = [
    "english",
    "uzbek", 
    "russian",
]

AUDIO_LANGUAGES = [
    "auto",
    "en",
    "uz", 
    "ru",
]

# User roles list for backward compatibility
USER_ROLES_LIST = [
    "user",
    "admin",
    "super_admin"
]

# Service configuration
SERVICE_ENDPOINTS = {
    "main": "https://www.saytoai.org",
    "api": "https://api.saytoai.org", 
    "admin": "https://admin.saytoai.org",
    "admin_api": "https://admin-api.saytoai.org"
}

# Validation constants
MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 50

# Rate limiting constants
DEFAULT_RATE_LIMIT_PER_MINUTE = 10
DEFAULT_RATE_LIMIT_PER_HOUR = 100
DEFAULT_RATE_LIMIT_PER_DAY = 1000

# Cache expiration times (in seconds)
CACHE_EXPIRATION = {
    "user_profile": 300,      # 5 minutes
    "user_credits": 60,       # 1 minute
    "system_status": 30,      # 30 seconds
    "api_keys": 600,          # 10 minutes
    "email_codes": 600,       # 10 minutes
}

# Error messages
ERROR_MESSAGES = {
    "user_not_found": "User not found",
    "insufficient_credits": "Insufficient credits",
    "invalid_subscription": "Invalid subscription",
    "payment_failed": "Payment processing failed",
    "service_unavailable": "Service temporarily unavailable",
    "rate_limit_exceeded": "Rate limit exceeded",
    "unauthorized_access": "Unauthorized access",
    "invalid_request": "Invalid request format",
    "invalid_email": "Invalid email format",
    "invalid_password": "Password does not meet requirements",
    "email_not_verified": "Email address not verified",
    "invalid_verification_code": "Invalid or expired verification code",
    "account_locked": "Account temporarily locked due to too many failed attempts",
}

# Success messages  
SUCCESS_MESSAGES = {
    "user_created": "User successfully created",
    "payment_completed": "Payment completed successfully",
    "subscription_updated": "Subscription updated",
    "profile_updated": "Profile updated successfully",
    "email_verified": "Email successfully verified",
    "password_reset": "Password successfully reset",
    "verification_code_sent": "Verification code sent to your email",
}

# Feature flags (for enabling/disabling features across services)
FEATURES = {
    "payment_enabled": True,
    "audio_processing_enabled": True,
    "multi_language_enabled": True,
    "rate_limiting_enabled": True,
    "caching_enabled": True,
    "email_verification_enabled": True,
    "password_reset_enabled": True,
}

# Prompt and role management constants
MAX_CUSTOM_PROMPT_COUNT = 1  # Default limit for basic users
MAX_CUSTOM_PROMPT_LENGTH = 4000

# Enhanced role system limits
ROLE_PROMPT_LIMITS = {
    "user": 1,        # Basic users: 1 custom prompt
    "admin": 5,       # Admins: 5 custom prompts  
    "super_admin": 10 # Super admins: 10 custom prompts
}

ROLE_CREDIT_LIMITS = {
    "user": 50,       # Basic users: 50 credits/month
    "admin": 500,     # Admins: 500 credits/month
    "super_admin": 1000  # Super admins: 1000 credits/month
}

# Prompt contexts - different scenarios where prompts are used
PROMPT_CONTEXTS = [
    "developer",
    "designer", 
    "ai_chat"
]

# Default prompt templates
DEFAULT_PROMPTS = {
    "developer": DEVELOPER_PROMPT,
    "designer": DESIGNER_PROMPT,
    "ai_chat": AI_CHAT_PROMPT
}

# Validation rules for prompts
PROMPT_VALIDATION = {
    "min_length": 10,
    "max_length": MAX_CUSTOM_PROMPT_LENGTH,
}

# Role-based feature flags
ROLE_FEATURES = {
    "user": {
        "custom_prompts": True,
        "multiple_contexts": False,
        "prompt_templates": True,
        "usage_analytics": False,
        "role_management": False
    },
    "admin": {
        "custom_prompts": True,
        "multiple_contexts": True,
        "prompt_templates": True,
        "usage_analytics": True,
        "role_management": False
    },
    "super_admin": {
        "custom_prompts": True,
        "multiple_contexts": True,
        "prompt_templates": True,
        "usage_analytics": True,
        "role_management": True
    }
}

# ===== EMAIL VALIDATION & ABUSE PREVENTION =====

# Allowed email providers (only these are permitted)
ALLOWED_EMAIL_PROVIDERS = {
    # Major international providers
    "gmail.com", "googlemail.com", "google.com",
    "outlook.com", "hotmail.com", "live.com", "msn.com",
    "yahoo.com", "yahoo.co.uk", "yahoo.ca", "yahoo.fr", "yahoo.de",
    "icloud.com", "me.com", "mac.com",
    
    # Russian/CIS providers
    "mail.ru", "bk.ru", "inbox.ru", "list.ru",
    "yandex.ru", "yandex.com", "ya.ru",
    
    # Other major providers
    "aol.com", "protonmail.com", "tutanota.com",
    "zoho.com", "fastmail.com"
}

# Trusted email providers (major legitimate providers) - keeping for backward compatibility
TRUSTED_EMAIL_PROVIDERS = ALLOWED_EMAIL_PROVIDERS

# Email validation rules
EMAIL_VALIDATION_RULES = {
    "require_trusted_provider": True,  # Only allow trusted providers
    "check_mx_record": False,         # Check if domain has MX record (optional)
    "case_sensitive": False,          # Email comparison case sensitivity
    "max_local_length": 64,           # Maximum length of local part (before @)
    "max_domain_length": 253          # Maximum length of domain part
}

# Email validation error messages
EMAIL_VALIDATION_MESSAGES = {
    "invalid_format": "Please enter a valid email address",
    "untrusted_provider": "Please use an email from a recognized provider (Gmail, Outlook, Yahoo, etc.)",
    "forbidden_email": "⚠️ This email provider is not supported by our platform. Please use one of the allowed email providers: Gmail, Outlook, Yahoo, Mail.ru, Yandex, or other major providers.",
    "domain_too_new": "Email domain appears to be too new. Please use an established email provider.",
    "no_mx_record": "Email domain does not appear to accept emails",
    "local_too_long": "Email address username is too long",
    "domain_too_long": "Email domain is too long",
    "blocked_domain": "This email provider is not allowed for registration"
}

# Additional validation patterns
EMAIL_VALIDATION_PATTERNS = {
    "suspicious_patterns": [
        r"^[a-z]+\d+@",           # Simple pattern like user123@
        r"^\d+[a-z]*@",           # Starts with numbers
        r"^test\d*@",             # Test emails
        r"^temp\d*@",             # Temp emails
        r"^fake\d*@",             # Fake emails
        r"^spam\d*@",             # Spam emails
        r"^noreply@",             # No-reply emails
        r"^no-reply@",            # No-reply emails
    ],
    "allowed_special_chars": ".-_+",  # Allowed special characters in local part
    "min_local_length": 1,            # Minimum length before @
    "require_dot_in_domain": True     # Domain must contain at least one dot
}

# ===== SMS VERIFICATION & PHONE AUTHENTICATION =====

# SMS verification constants
SMS_CODE_LENGTH = 6
SMS_CODE_EXPIRATION_MINUTES = 5
MAX_SMS_ATTEMPTS_PER_HOUR = 3
MAX_SMS_VERIFICATION_ATTEMPTS = 3
SMS_RESEND_COOLDOWN_SECONDS = 60

# SMS service configuration
SMS_SERVICE_CONFIG = {
    "provider": "eskiz.uz",
    "cost_per_sms": 95,  # 95 so'm per SMS
    "currency": "UZS",
    "max_daily_sms": 10,  # Daily SMS limit per user
    "rate_limit_per_minute": 2  # SMS rate limiting
}

# Phone number validation
PHONE_VALIDATION_RULES = {
    "min_length": 8,
    "max_length": 15,
    "require_plus_prefix": True,        # Must start with +
    "min_digits": 7,                    # Minimum number of digits after +
    "max_digits": 14,                   # Maximum number of digits after +
    "allow_spaces": False,              # Don't allow spaces in validation
    "allow_dashes": False,              # Don't allow dashes in validation
    "allow_parentheses": False          # Don't allow parentheses in validation
}

# SMS verification error messages
SMS_VALIDATION_MESSAGES = {
    "invalid_phone_format": "Please enter a valid phone number starting with + followed by 7-14 digits",
    "phone_too_short": "Phone number must have at least 7 digits after the country code",
    "phone_too_long": "Phone number cannot exceed 14 digits after the country code",
    "missing_plus_prefix": "Phone number must start with + followed by country code",
    "invalid_characters": "Phone number can only contain + and digits",
    "too_many_repeated_digits": "Phone number contains too many repeated digits",
    "sms_rate_limit": "Too many SMS requests. Please wait before requesting another code",
    "sms_send_failed": "Failed to send SMS. Please confirm if you want to retry or contact support",
    "sms_send_failed_retry": "SMS delivery failed again. Please contact admin for manual verification",
    "user_confirmation_timeout": "Confirmation timeout. Please start the verification process again",
    "max_retry_attempts": "Maximum retry attempts reached. Please contact admin for assistance",
    "invalid_sms_code": "Invalid or expired SMS verification code",
    "max_attempts_exceeded": "Maximum verification attempts exceeded. Please request a new code",
    "phone_already_verified": "This phone number is already verified",
    "phone_already_registered": "This phone number is already registered to another account",
    "admin_review_required": "Your phone verification requires admin review. Support will contact you shortly",
    "verification_discarded": "Verification attempt was discarded due to timeout. Please try again"
}

# SMS templates
SMS_TEMPLATES = {
    "verification_code": "SayToAI code: {code}. Valid {minutes}min. Don't share.",
    "welcome_sms": "Welcome to SayToAI! Account created successfully.",
    "password_reset": "SayToAI reset: {code}. Valid {minutes}min.",
    "login_notification": "SayToAI login from {device}. Secure account if not you.",
    "alert_notification": "SayToAI Alert: {alert_type} - {summary}. Check dashboard.",
    "critical_alert": "🚨 CRITICAL: {service} - {summary}",
    "system_alert": "🖥️ SYSTEM: {alert_count} alerts. {summary}",
    "container_alert": "🐳 CONTAINER: {container_count} affected. {alert_type}",
    "database_alert": "🗄️ DB: {database} - {summary}",
    "generic_alert": "{icon} {alert_type}: {summary}"
}

# Registration method types
class RegistrationMethod(str, Enum):
    """Registration method types."""
    EMAIL_ONLY = "email_only"
    PHONE_ONLY = "phone_only"
    EMAIL_AND_PHONE = "email_and_phone"
    TELEGRAM_LINK = "telegram_link"

# SMS delivery method types
class SMSDeliveryMethod(str, Enum):
    """SMS delivery method types."""
    TELEGRAM_BOT = "telegram_bot"
    EXTERNAL_SMS = "external_sms"
    FALLBACK = "fallback"

# SMS delivery status types
class SMSDeliveryStatus(str, Enum):
    """SMS delivery status types."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"
    UNKNOWN = "unknown"

# Phone verification status
class PhoneVerificationStatus(str, Enum):
    """Phone verification status."""
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    EXPIRED = "expired"

# SMS code purpose types
class SMSCodePurpose(str, Enum):
    """SMS verification code purposes."""
    REGISTRATION = "registration"
    LOGIN = "login"
    PASSWORD_RESET = "password_reset"

# ===== ANTI-FRAUD & USER VALIDATION SYSTEM =====

# Tiered credit system based on registration platform
PLATFORM_CREDIT_ALLOCATION = {
    "web": 20,        # Web registration: 20 credits (lower trust)
    "telegram": 50,   # Telegram registration: 50 credits (higher trust)
    "admin": 1000     # Admin created accounts: 1000 credits
}

# IP-based rate limiting for fraud prevention
IP_RATE_LIMITS = {
    "registration_attempts_per_minute": 2,    # Max 2 registration attempts per minute per IP
    "registration_attempts_per_day": 10,      # Max 10 registration attempts per day per IP
    "sms_requests_per_minute": 2,             # Max 2 SMS requests per minute per IP
    "sms_requests_per_day": 5,                # Max 5 SMS requests per day per IP
    "email_verification_per_minute": 3,       # Max 3 email verifications per minute per IP
    "email_verification_per_day": 15,         # Max 15 email verifications per day per IP
    "login_attempts_per_minute": 5,           # Max 5 login attempts per minute per IP
    "login_attempts_per_hour": 20,            # Max 20 login attempts per hour per IP
    "password_reset_per_hour": 3,             # Max 3 password resets per hour per IP
    "password_reset_per_day": 10              # Max 10 password resets per day per IP
}

# CAPTCHA configuration
CAPTCHA_CONFIG = {
    "enabled": True,
    "provider": "recaptcha_v3",  # recaptcha_v2, recaptcha_v3, hcaptcha
    "site_key": None,            # To be set in environment
    "secret_key": None,          # To be set in environment
    "score_threshold": 0.5,      # Minimum score for reCAPTCHA v3 (0.0-1.0)
    "required_for": [
        "web_registration",
        "password_reset",
        "multiple_failed_attempts",
        "suspicious_ip"
    ],
    "bypass_for_telegram": True,  # Skip CAPTCHA for Telegram users
    "challenge_after_failures": 3  # Show CAPTCHA after 3 failed attempts
}

# Enhanced phone validation for fraud prevention
ENHANCED_PHONE_VALIDATION = {
    "require_mobile_only": False,             # Allow all phone types
    "block_voip_numbers": False,              # Don't block VoIP numbers
    "require_carrier_validation": False,      # Skip carrier validation
    "validate_number_exists": False,          # Don't check if number actually exists
    "check_number_type": False,               # Don't verify phone type
    "min_unique_digits": 3                    # Minimum unique digits required
}

# User behavior analysis for fraud detection
FRAUD_DETECTION_RULES = {
    "max_accounts_per_ip_per_day": 3,         # Max accounts created per IP per day
    "max_accounts_per_device_per_week": 2,    # Max accounts per device fingerprint per week
    "device_fingerprint_required": True,      # Require device fingerprinting
    "track_user_agent_changes": True,         # Track suspicious UA changes
    "monitor_registration_speed": True,       # Monitor how fast forms are filled
    "min_registration_time_seconds": 30,      # Minimum time to fill registration form
    "max_registration_time_minutes": 30       # Maximum reasonable time
}

# Account verification levels
class AccountVerificationLevel(str, Enum):
    """Account verification levels for fraud prevention."""
    UNVERIFIED = "unverified"           # Just created, no verification
    EMAIL_VERIFIED = "email_verified"   # Email verified only
    PHONE_VERIFIED = "phone_verified"   # Phone verified only
    FULLY_VERIFIED = "fully_verified"   # Both email and phone verified
    PREMIUM_VERIFIED = "premium_verified" # Additional verification (ID, etc.)

# Simplified risk scoring system
RISK_SCORING = {
    "low_risk_threshold": 0.3,      # Below this = low risk
    "medium_risk_threshold": 0.6,   # Between low and this = medium risk
    "high_risk_threshold": 0.8,     # Above this = high risk, block registration
}

# Verification requirements based on risk level
VERIFICATION_REQUIREMENTS = {
    "low_risk": {
        "email_verification": True,
        "phone_verification": False,
        "captcha_required": False,
        "manual_review": False,
        "additional_verification": False
    },
    "medium_risk": {
        "email_verification": True,
        "phone_verification": True,
        "captcha_required": True,
        "manual_review": False,
        "additional_verification": False
    },
    "high_risk": {
        "email_verification": True,
        "phone_verification": True,
        "captcha_required": True,
        "manual_review": True,
        "additional_verification": True
    }
}

# Fraud prevention error messages
FRAUD_PREVENTION_MESSAGES = {
    "ip_rate_limit_exceeded": "Too many registration attempts from your location. Please try again later.",
    "suspicious_phone_number": "This phone number appears to be invalid or suspicious. Please use a valid mobile number.",
    "suspicious_email_pattern": "Please use a valid personal email address.",
    "captcha_required": "Please complete the security verification to continue.",
    "captcha_failed": "Security verification failed. Please try again.",
    "high_risk_account": "Your registration requires additional verification. Please contact support.",
    "device_fingerprint_required": "Unable to verify your device. Please enable JavaScript and try again.",
    "registration_too_fast": "Please take your time filling out the registration form.",
    "multiple_accounts_detected": "Multiple accounts detected from your location. Please contact support if you need assistance.",
    "blocked_ip": "Registration is not available from your location. Please contact support.",
    "suspicious_activity": "Suspicious activity detected. Your registration requires manual review.",
    "verification_required": "Additional verification is required to complete your registration."
}

# Fraud detection actions
class FraudDetectionAction(str, Enum):
    """Actions to take when fraud is detected."""
    ALLOW = "allow"                    # Allow registration
    REQUIRE_CAPTCHA = "require_captcha" # Require CAPTCHA verification
    REQUIRE_PHONE = "require_phone"    # Require phone verification
    REQUIRE_MANUAL_REVIEW = "require_manual_review" # Flag for manual review
    BLOCK_REGISTRATION = "block_registration" # Block registration completely
    TEMPORARY_BLOCK = "temporary_block" # Temporary block (24 hours)

# Simplified IP geolocation risk assessment
IP_GEOLOCATION_RISK = {
    "vpn_detection_enabled": True,
    "proxy_detection_enabled": True,
    "tor_detection_enabled": True,
    "datacenter_detection_enabled": True
}

# Device fingerprinting configuration
DEVICE_FINGERPRINTING = {
    "enabled": True,
    "required_fields": [
        "user_agent",
        "screen_resolution",
        "timezone",
        "language",
        "platform"
    ],
    "optional_fields": [
        "canvas_fingerprint",
        "webgl_fingerprint",
        "audio_fingerprint",
        "font_list",
        "plugins_list"
    ],
    "fingerprint_expiry_days": 30,
    "max_accounts_per_fingerprint": 2
}

# Account monitoring and cleanup
ACCOUNT_MONITORING = {
    "inactive_account_days": 90,           # Days before account is considered inactive
    "suspicious_account_review_days": 7,   # Days to review suspicious accounts
    "auto_cleanup_fake_accounts": True,    # Automatically clean up detected fake accounts
    "credit_abuse_threshold": 5,           # Number of accounts before investigating credit abuse
    "monitor_credit_usage_patterns": True, # Monitor unusual credit usage
    "flag_rapid_credit_consumption": True  # Flag accounts that use credits too quickly
}

# SMS verification workflow constants
SMS_VERIFICATION_WORKFLOW = {
    "user_confirmation_timeout_minutes": 7,    # Wait 7 minutes for user confirmation
    "max_retry_attempts": 2,                    # Maximum retry attempts
    "retry_cooldown_minutes": 2,                # Cooldown between retries
    "admin_override_enabled": True,             # Allow admin manual verification
    "auto_discard_failed_attempts": True,       # Auto-discard after timeout
    "send_failure_notifications": True,         # Notify admins of failures
    "track_delivery_status": True               # Track SMS delivery status
}

# SMS verification statuses
class SMSVerificationWorkflowStatus(str, Enum):
    """SMS verification workflow statuses."""
    PENDING = "pending"                         # SMS sent, waiting for verification
    AWAITING_CONFIRMATION = "awaiting_confirmation"  # SMS failed, waiting for user confirmation
    USER_CONFIRMED = "user_confirmed"           # User confirmed they want to retry
    RETRY_SCHEDULED = "retry_scheduled"         # Retry attempt scheduled
    FAILED_FINAL = "failed_final"              # All attempts failed
    ADMIN_REVIEW = "admin_review"              # Requires admin intervention
    ADMIN_VERIFIED = "admin_verified"          # Manually verified by admin
    COMPLETED = "completed"                     # Successfully verified
    DISCARDED = "discarded"                     # Attempt discarded due to timeout

# Admin verification actions
class AdminVerificationAction(str, Enum):
    """Admin actions for manual phone verification."""
    MANUAL_VERIFY = "manual_verify"            # Manually verify the phone number
    MARK_INVALID = "mark_invalid"              # Mark phone as invalid
    REQUEST_ALTERNATIVE = "request_alternative" # Request alternative contact method
    ESCALATE_SUPPORT = "escalate_support"      # Escalate to higher support level
    ADD_TO_WHITELIST = "add_to_whitelist"      # Add to trusted numbers list

# ===== PAYMENT SYSTEM CONSTANTS =====

# Payment provider configurations - updated to match voiceBot structure
PAYMENT_PROVIDERS = {
    "payme": {
        "name": "Payme",
        "currency": "UZS",
        "min_amount": 2500000,    # 2,500,000 UZS (in tiyin)
        "max_amount": 10000000,  # 10,000,000 UZS (in tiyin)
        "fee_percentage": 0.0,   # No fee for users
        "supported_methods": ["card"],
        "base_url": "https://checkout.paycom.uz"
    },
    "click": {
        "name": "Click",
        "currency": "UZS", 
        "min_amount": 25000,      # 25000 UZS
        "max_amount": 100000,  # 100,000 UZS
        "fee_percentage": 0.0,   # No fee for users
        "supported_methods": ["card", "wallet"],
        "base_url": "https://my.click.uz/services/pay"
    }
}

# Tariff configurations - matching voiceBot structure
PAYMENT_TARIFFS = {
    "basic": {
        "amount": 2500000,    # 2,500,000 UZS (in tiyin)
        "credits": 60,
        "name": "Basic Plan",
        "description": "60 credits for basic usage"
    },
    "standard": {
        "amount": 5000000,   # 50,000 UZS (in tiyin)
        "credits": 140,
        "name": "Standard Plan", 
        "description": "140 credits for regular usage"
    },
    "premium": {
        "amount": 10000000,  # 100,000 UZS (in tiyin)
        "credits": 300,
        "name": "Premium Plan",
        "description": "300 credits for heavy usage"
    }
}

# Payment limits and validation - updated for tiyin amounts
PAYMENT_LIMITS = {
    "min_amount_uzs": 2500000,      # 2,500,000 UZS minimum
    "max_amount_uzs": 10000000,  # 10,000,000 UZS maximum
    "daily_limit_uzs": 5000000,  # 5,000,000 UZS daily limit
    "monthly_limit_uzs": 50000000, # 50,000,000 UZS monthly limit
    "min_amount_tiyin": 250000000,  # 2,500,000 UZS in tiyin (multiply by 100)
    "max_amount_tiyin": 1000000000, # 10,000,000 UZS in tiyin
}

# Payment error codes
PAYMENT_ERROR_CODES = {
    "INVALID_AMOUNT": "Payment amount is invalid",
    "INSUFFICIENT_FUNDS": "Insufficient funds",
    "CARD_EXPIRED": "Card has expired",
    "CARD_BLOCKED": "Card is blocked",
    "INVALID_CARD": "Invalid card details",
    "TRANSACTION_DECLINED": "Transaction declined by bank",
    "NETWORK_ERROR": "Network connection error",
    "PROVIDER_ERROR": "Payment provider error",
    "SIGNATURE_INVALID": "Invalid signature",
    "ORDER_NOT_FOUND": "Order not found",
    "DUPLICATE_TRANSACTION": "Duplicate transaction",
    "AMOUNT_MISMATCH": "Amount mismatch"
}

# Payment success messages
PAYMENT_SUCCESS_MESSAGES = {
    "payment_initiated": "Payment initiated successfully",
    "payment_completed": "Payment completed successfully", 
    "refund_processed": "Refund processed successfully",
    "subscription_activated": "Subscription activated",
    "credits_added": "Credits added to your account"
}