"""
Authentication-related Pydantic schemas for SayToAI ecosystem.
Handles email/password auth with verification codes.
"""

import re
from pydantic import BaseModel, Field, validator # type: ignore
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..constants import (
    AuthMethod,
    EmailCodePurpose,
    PASSWORD_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    EMAIL_CODE_LENGTH,
    RegistrationMethod
)
from ..utils import validate_email_for_registration, validate_phone_number

# Email regex pattern for validation
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

class PasswordValidatorMixin(BaseModel):
    """Shared password validation logic."""
    
    @validator("password", check_fields=False)
    def validate_password(cls, v):
        if len(v) < PASSWORD_MIN_LENGTH:
            raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
        if len(v) > PASSWORD_MAX_LENGTH:
            raise ValueError(f"Password must not exceed {PASSWORD_MAX_LENGTH} characters")
        
        # Add more complex password rules if needed
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        
        return v

class EmailValidatorMixin(BaseModel):
    """Shared email validation logic."""
    
    @validator("email", check_fields=False)
    def validate_email(cls, v):
        if not EMAIL_REGEX.match(v):
            raise ValueError("Invalid email format")
        return v.lower()  # Normalize to lowercase

class RegistrationRequest(EmailValidatorMixin, PasswordValidatorMixin):
    """Schema for user registration via email."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    first_name: Optional[str] = Field(default=None, description="User's first name")

class EmailVerificationRequest(EmailValidatorMixin):
    """Schema for requesting email verification code."""
    email: str = Field(..., description="Email address to verify")
    purpose: EmailCodePurpose = Field(description="Purpose of verification code")

class EmailVerificationConfirm(EmailValidatorMixin):
    """Schema for confirming email verification with code."""
    email: str = Field(..., description="Email address")
    code: str = Field(..., min_length=EMAIL_CODE_LENGTH, max_length=EMAIL_CODE_LENGTH, description="Verification code")
    
    @validator("code")
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError("Verification code must contain only digits")
        return v

class LoginRequest(EmailValidatorMixin):
    """Schema for user login."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")

class ForgotPasswordRequest(EmailValidatorMixin):
    """Schema for requesting password reset."""
    email: str = Field(..., description="Email address for password reset")

class ResetPasswordConfirm(EmailValidatorMixin, PasswordValidatorMixin):
    """Schema for confirming password reset with code."""
    email: str = Field(..., description="Email address")
    code: str = Field(..., min_length=EMAIL_CODE_LENGTH, max_length=EMAIL_CODE_LENGTH, description="Reset code")
    new_password: str = Field(..., description="New password")
    
    @validator("code")
    def validate_code(cls, v):
        if not v.isdigit():
            raise ValueError("Reset code must contain only digits")
        return v

class ChangePasswordRequest(PasswordValidatorMixin):
    """Schema for changing password (when logged in)."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password")

class AuthToken(BaseModel):
    """Schema for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    refresh_token: Optional[str] = Field(default=None, description="Optional refresh token")

class UserSession(BaseModel):
    """Schema for user session information."""
    user_id: int = Field(..., description="User identifier")
    email: str = Field(..., description="User email")
    is_verified: bool = Field(..., description="Email verification status")
    auth_method: AuthMethod = Field(..., description="Authentication method used")
    session_id: str = Field(..., description="Session identifier")
    created_at: datetime = Field(..., description="Session creation time")
    expires_at: datetime = Field(..., description="Session expiration time")

class EmailCode(BaseModel):
    """Schema for email verification code storage."""
    email: str = Field(..., description="Email address")
    code: str = Field(..., description="Verification code")
    purpose: EmailCodePurpose = Field(..., description="Code purpose")
    expires_at: datetime = Field(..., description="Code expiration time")
    created_at: datetime = Field(default_factory=datetime.now, description="Code creation time")
    attempts: int = Field(default=0, description="Number of verification attempts")
    max_attempts: int = Field(default=3, description="Maximum allowed attempts")

class LoginAttempt(BaseModel):
    """Schema for tracking login attempts."""
    email: str = Field(..., description="Email address")
    ip_address: str = Field(..., description="IP address of attempt")
    user_agent: Optional[str] = Field(default=None, description="User agent string")
    success: bool = Field(..., description="Whether attempt was successful")
    failure_reason: Optional[str] = Field(default=None, description="Reason for failure")
    timestamp: datetime = Field(default_factory=datetime.now, description="Attempt timestamp")

class AccountLockout(BaseModel):
    """Schema for account lockout information."""
    email: str = Field(..., description="Locked email address")
    locked_at: datetime = Field(..., description="Lockout timestamp")
    expires_at: datetime = Field(..., description="Lockout expiration")
    failed_attempts: int = Field(..., description="Number of failed attempts")
    reason: str = Field(..., description="Lockout reason")

class SecurityEvent(BaseModel):
    """Schema for security-related events."""
    user_id: Optional[int] = Field(default=None, description="User ID if applicable")
    email: Optional[str] = Field(default=None, description="Email if applicable")
    event_type: str = Field(..., description="Type of security event")
    ip_address: str = Field(..., description="IP address")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    details: Optional[dict] = Field(default=None, description="Additional event details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Event timestamp")
    severity: str = Field(default="info", description="Event severity level")

# Response schemas
class RegistrationResponse(BaseModel):
    """Response after successful registration."""
    message: str = Field(..., description="Success message")
    email: str = Field(..., description="Registered email")
    verification_required: bool = Field(default=True, description="Whether email verification is required")

class LoginResponse(BaseModel):
    """Response after successful login."""
    user: UserSession = Field(..., description="User session information")
    tokens: AuthToken = Field(..., description="Authentication tokens")

class VerificationResponse(BaseModel):
    """Response after email verification."""
    message: str = Field(..., description="Success message")
    email: str = Field(..., description="Verified email")
    verified: bool = Field(..., description="Verification status")

class PasswordResetResponse(BaseModel):
    """Response after password reset."""
    message: str = Field(..., description="Success message")
    email: str = Field(..., description="Email address")
    reset_successful: bool = Field(..., description="Reset status")

class UserRegistrationRequest(BaseModel):
    """Enhanced user registration with email validation."""
    email: str = Field(description="User email address")
    password: str = Field(min_length=8, max_length=128, description="User password")
    confirm_password: str = Field(description="Password confirmation")
    language: str = Field(default="english", description="Preferred language")
    terms_accepted: bool = Field(description="Terms and conditions acceptance")
    marketing_consent: bool = Field(default=False, description="Marketing emails consent")
    
    # Anti-abuse fields
    referral_code: Optional[str] = Field(default=None, description="Referral code if any")
    signup_source: str = Field(default="web", description="Registration source")
    
    @validator('email')
    def validate_email_address(cls, v):
        """Validate email against disposable providers and ensure trusted domain."""
        validation_result = validate_email_for_registration(v, strict_mode=True)
        
        if not validation_result["is_valid"]:
            raise ValueError(validation_result["message"])
        
        return v.lower().strip()
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('terms_accepted')
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v

class EmailValidationRequest(BaseModel):
    """Request to validate an email address."""
    email: str = Field(description="Email address to validate")
    strict_mode: bool = Field(default=True, description="Use strict validation")
    check_abuse: bool = Field(default=True, description="Check for abuse patterns")

class EmailValidationResponse(BaseModel):
    """Response for email validation."""
    is_valid: bool = Field(description="Whether email is valid")
    error_code: Optional[str] = Field(default=None, description="Error code if invalid")
    message: str = Field(description="Validation message")
    
    # Provider information
    provider_info: dict = Field(description="Email provider details")
    is_trusted_provider: bool = Field(description="Whether provider is trusted")
    is_disposable: bool = Field(description="Whether email is disposable")
    
    # Abuse detection
    abuse_score: Optional[int] = Field(default=None, description="Abuse risk score (0-100)")
    abuse_flags: List[str] = Field(default_factory=list, description="Abuse indicators")
    
    # Suggestions
    alternative_providers: Optional[List[dict]] = Field(default=None, description="Alternative providers if blocked")

class RegistrationAttemptLog(BaseModel):
    """Log registration attempts for abuse detection."""
    id: Optional[int] = Field(default=None)
    
    # Attempt details
    email: str = Field(description="Email used in attempt")
    normalized_email: str = Field(description="Normalized email for comparison")
    ip_address: str = Field(description="IP address of attempt")
    user_agent: str = Field(description="User agent string")
    
    # Validation results
    email_validation_result: dict = Field(description="Email validation results")
    was_blocked: bool = Field(description="Whether attempt was blocked")
    block_reason: Optional[str] = Field(default=None, description="Reason for blocking")
    
    # Abuse detection
    abuse_score: int = Field(ge=0, le=100, description="Calculated abuse score")
    abuse_flags: List[str] = Field(default_factory=list, description="Abuse indicators found")
    
    # Geographic and device info
    country_code: Optional[str] = Field(default=None, description="Country from IP")
    device_fingerprint: Optional[str] = Field(default=None, description="Device fingerprint")
    
    # Timing
    attempt_timestamp: datetime = Field(default_factory=datetime.now)
    session_id: Optional[str] = Field(default=None, description="Session identifier")

class EmailProviderStats(BaseModel):
    """Statistics about email provider usage."""
    provider_domain: str = Field(description="Email provider domain")
    
    # Usage statistics
    total_registrations: int = Field(ge=0, description="Total registrations from this provider")
    successful_registrations: int = Field(ge=0, description="Successful registrations")
    blocked_attempts: int = Field(ge=0, description="Blocked registration attempts")
    
    # Quality metrics
    average_abuse_score: float = Field(ge=0.0, le=100.0, description="Average abuse score")
    spam_reports: int = Field(ge=0, description="Number of spam reports")
    account_suspensions: int = Field(ge=0, description="Accounts suspended")
    
    # Provider classification
    is_trusted: bool = Field(description="Whether provider is trusted")
    is_disposable: bool = Field(description="Whether provider is disposable")
    provider_type: str = Field(description="Provider category")
    
    # Time tracking
    first_seen: datetime = Field(description="First registration from this provider")
    last_seen: datetime = Field(description="Most recent registration")
    
    # Risk assessment
    risk_level: str = Field(description="Overall risk level (low/medium/high)")
    auto_block: bool = Field(default=False, description="Whether to auto-block this provider")

class AbusePreventionSettings(BaseModel):
    """Configuration for abuse prevention system."""
    
    # Email validation settings
    require_trusted_providers: bool = Field(default=True, description="Only allow trusted providers")
    # Note: Disposable email blocking removed - using allowlist approach
    allow_plus_addressing: bool = Field(default=True, description="Allow gmail+tag format")
    
    # Abuse detection thresholds
    max_abuse_score: int = Field(default=50, ge=0, le=100, description="Maximum allowed abuse score")
    auto_block_threshold: int = Field(default=75, ge=0, le=100, description="Auto-block threshold")
    manual_review_threshold: int = Field(default=30, ge=0, le=100, description="Manual review threshold")
    
    # Rate limiting
    max_attempts_per_ip_hour: int = Field(default=5, ge=1, description="Max attempts per IP per hour")
    max_attempts_per_email_day: int = Field(default=3, ge=1, description="Max attempts per email per day")
    
    # Geographic restrictions
    blocked_countries: List[str] = Field(default_factory=list, description="Blocked country codes")
    allowed_countries: List[str] = Field(default_factory=list, description="Allowed countries (if set, only these)")
    
    # Additional security
    require_email_verification: bool = Field(default=True, description="Require email verification")
    verification_code_expiry_minutes: int = Field(default=15, ge=1, description="Verification code expiry")
    max_verification_attempts: int = Field(default=3, ge=1, description="Max verification attempts")

# Enhanced registration response with abuse prevention info
class UserRegistrationResponse(BaseModel):
    """Enhanced registration response."""
    success: bool = Field(description="Whether registration was successful")
    message: str = Field(description="Response message")
    
    # User information (if successful)
    user_id: Optional[int] = Field(default=None, description="Created user ID")
    email: Optional[str] = Field(default=None, description="Registered email")
    
    # Email verification
    verification_required: bool = Field(description="Whether email verification is required")
    verification_code_sent: bool = Field(default=False, description="Whether verification code was sent")
    
    # Security information
    email_validation: dict = Field(description="Email validation results")
    abuse_prevention: dict = Field(description="Abuse prevention information")
    
    # Next steps
    next_steps: List[str] = Field(description="What user should do next")
    estimated_verification_time: Optional[int] = Field(default=None, description="Expected verification time in minutes")

# ===== SMS VERIFICATION & PHONE AUTHENTICATION =====

class PhoneLoginRequest(BaseModel):
    """Request for phone number login with SMS verification."""
    phone: str = Field(description="Phone number with country code")
    language: str = Field(default="english", description="Preferred language")
    
    # Device and session info
    device_info: Optional[str] = Field(default=None, description="Device information")
    user_agent: Optional[str] = Field(default=None, description="User agent string")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    
    @validator('phone')
    def validate_phone_number(cls, v):
        """Validate phone number format and country support."""
        validation_result = validate_phone_number(v)
        
        if not validation_result["is_valid"]:
            raise ValueError(validation_result["message"])
        
        return validation_result["formatted_phone"]

class CombinedRegistrationRequest(BaseModel):
    """Request for combined email + phone registration."""
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number with country code")
    password: str = Field(min_length=8, max_length=128, description="Password")
    language: str = Field(default="english", description="Preferred language")
    terms_accepted: bool = Field(description="Terms and conditions acceptance")
    marketing_consent: bool = Field(default=False, description="Marketing consent")
    
    # Device and session info
    device_info: Optional[str] = Field(default=None, description="Device information")
    user_agent: Optional[str] = Field(default=None, description="User agent string")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    
    @validator('email')
    def validate_email_format(cls, v):
        validation_result = validate_email_for_registration(v)
        
        if not validation_result["is_valid"]:
            raise ValueError(validation_result["message"])
        
        return validation_result["normalized_email"]
    
    @validator('phone')
    def validate_phone_number(cls, v):
        validation_result = validate_phone_number(v)
        
        if not validation_result["is_valid"]:
            raise ValueError(validation_result["message"])
        
        return validation_result["formatted_phone"]
    
    @validator('terms_accepted')
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v

class RegistrationMethodResponse(BaseModel):
    """Response indicating available registration methods."""
    email_registration: bool = Field(description="Whether email registration is available")
    phone_registration: bool = Field(description="Whether phone registration is available")
    combined_registration: bool = Field(description="Whether email+phone registration is available")
    telegram_link: bool = Field(description="Whether Telegram linking is available")
    
    # Method-specific information
    supported_countries: List[str] = Field(description="Supported country codes for phone registration")
    allowed_email_providers: List[str] = Field(description="Allowed email providers")
    
    # Requirements
    email_verification_required: bool = Field(description="Whether email verification is required")
    phone_verification_required: bool = Field(description="Whether phone verification is required")
    
    # Costs and limits
    sms_cost_info: Optional[Dict[str, Any]] = Field(default=None, description="SMS cost information")

class AuthenticationResponse(BaseModel):
    """Enhanced authentication response with SMS support."""
    success: bool = Field(description="Whether authentication was successful")
    message: str = Field(description="Response message")
    
    # Authentication details
    auth_method: str = Field(description="Authentication method used")
    requires_verification: bool = Field(description="Whether additional verification is needed")
    verification_type: Optional[str] = Field(default=None, description="Type of verification required")
    
    # User information (if authenticated)
    user_id: Optional[int] = Field(default=None, description="User ID")
    access_token: Optional[str] = Field(default=None, description="Access token")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    token_expires_in: Optional[int] = Field(default=None, description="Token expiry in seconds")
    
    # User profile
    user_profile: Optional[Dict[str, Any]] = Field(default=None, description="User profile information")
    
    # Next steps
    next_steps: List[str] = Field(description="What user should do next")
    verification_id: Optional[str] = Field(default=None, description="Verification session ID")
    
    # Error details (if authentication failed)
    error_code: Optional[str] = Field(default=None, description="Error code if failed")
    retry_after_seconds: Optional[int] = Field(default=None, description="Retry cooldown period")

class MultiFactorAuthRequest(BaseModel):
    """Request for multi-factor authentication."""
    primary_auth_token: str = Field(description="Primary authentication token")
    verification_method: str = Field(description="Verification method (sms, email)")
    
    # For SMS verification
    phone: Optional[str] = Field(default=None, description="Phone number for SMS")
    
    # For email verification
    email: Optional[str] = Field(default=None, description="Email for verification")
    
    # Context
    device_info: Optional[str] = Field(default=None, description="Device information")
    ip_address: Optional[str] = Field(default=None, description="IP address")

class MultiFactorAuthVerification(BaseModel):
    """Multi-factor authentication verification."""
    primary_auth_token: str = Field(description="Primary authentication token")
    verification_code: str = Field(description="Verification code")
    verification_method: str = Field(description="Verification method used")
    
    # Optional context
    device_info: Optional[str] = Field(default=None, description="Device information")
    remember_device: bool = Field(default=False, description="Remember this device")

class AccountRecoveryRequest(BaseModel):
    """Request for account recovery using phone or email."""
    recovery_method: str = Field(description="Recovery method (phone, email)")
    
    # Recovery identifiers
    phone: Optional[str] = Field(default=None, description="Phone number for recovery")
    email: Optional[str] = Field(default=None, description="Email for recovery")
    
    # Additional verification
    backup_questions: Optional[Dict[str, str]] = Field(default=None, description="Security questions")
    
    # Context
    device_info: Optional[str] = Field(default=None, description="Device information")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    
    @validator('recovery_method')
    def validate_recovery_method(cls, v):
        if v not in ['phone', 'email', 'both']:
            raise ValueError('Recovery method must be phone, email, or both')
        return v

class PasswordResetWithSMSRequest(BaseModel):
    """Password reset request using SMS verification."""
    phone: str = Field(description="Phone number for password reset")
    new_password: str = Field(min_length=8, max_length=128, description="New password")
    
    # Context
    device_info: Optional[str] = Field(default=None, description="Device information")
    ip_address: Optional[str] = Field(default=None, description="IP address")
    
    @validator('phone')
    def validate_phone_number(cls, v):
        validation_result = validate_phone_number(v)
        
        if not validation_result["is_valid"]:
            raise ValueError(validation_result["message"])
        
        return validation_result["formatted_phone"]

class AuthenticationSession(BaseModel):
    """Authentication session tracking."""
    id: Optional[int] = Field(default=None)
    session_id: str = Field(description="Unique session identifier")
    user_id: Optional[int] = Field(default=None, description="User ID if authenticated")
    
    # Authentication details
    auth_method: str = Field(description="Authentication method")
    auth_status: str = Field(description="Authentication status")
    
    # Verification tracking
    email_verified: bool = Field(default=False, description="Email verification status")
    phone_verified: bool = Field(default=False, description="Phone verification status")
    mfa_completed: bool = Field(default=False, description="Multi-factor auth status")
    
    # Session metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(description="Session expiry time")
    
    # Device and location
    device_info: Optional[str] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    
    # Security flags
    is_suspicious: bool = Field(default=False, description="Whether session is flagged as suspicious")
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Risk assessment score")
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session data")

class EnhancedRegistrationRequest(BaseModel):
    """Enhanced registration request with comprehensive fraud prevention."""
    # Basic registration data
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number with country code")
    password: Optional[str] = Field(default=None, min_length=8, max_length=128, description="Password")
    name: Optional[str] = Field(default=None, description="User name")
    
    # Registration method and platform
    registration_method: RegistrationMethod = Field(description="Registration method")
    platform: str = Field(description="Registration platform (web, telegram)")
    
    # Terms and consent
    terms_accepted: bool = Field(description="Terms and conditions acceptance")
    marketing_consent: bool = Field(default=False, description="Marketing consent")
    privacy_policy_accepted: bool = Field(description="Privacy policy acceptance")
    
    # Device and session information
    device_fingerprint: Optional[Dict[str, Any]] = Field(default=None, description="Device fingerprint data")
    user_agent: str = Field(description="User agent string")
    ip_address: str = Field(description="User IP address")
    screen_resolution: Optional[str] = Field(default=None, description="Screen resolution")
    timezone: Optional[str] = Field(default=None, description="User timezone")
    language: str = Field(default="english", description="Preferred language")
    
    # Timing information for bot detection
    form_start_time: Optional[datetime] = Field(default=None, description="When user started filling form")
    form_submit_time: datetime = Field(default_factory=datetime.now, description="When form was submitted")
    
    # CAPTCHA verification
    captcha_response: Optional[str] = Field(default=None, description="CAPTCHA response token")
    captcha_type: Optional[str] = Field(default="recaptcha_v3", description="CAPTCHA type")
    
    # Additional context
    referrer: Optional[str] = Field(default=None, description="HTTP referrer")
    utm_source: Optional[str] = Field(default=None, description="UTM source")
    utm_medium: Optional[str] = Field(default=None, description="UTM medium")
    utm_campaign: Optional[str] = Field(default=None, description="UTM campaign")
    
    @validator('email')
    def validate_email_if_provided(cls, v):
        if v:
            from ..utils import validate_email_for_registration
            validation_result = validate_email_for_registration(v)
            if not validation_result["is_valid"]:
                raise ValueError(validation_result["message"])
            return validation_result["normalized_email"]
        return v
    
    @validator('phone')
    def validate_phone_if_provided(cls, v):
        if v:
            from ..utils import enhanced_phone_validation
            validation_result = enhanced_phone_validation(v)
            if not validation_result["is_valid"]:
                raise ValueError(validation_result["message"])
            return validation_result["formatted_phone"]
        return v
    
    @validator('terms_accepted', 'privacy_policy_accepted')
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('Terms and conditions and privacy policy must be accepted')
        return v
    
    @validator('registration_method')
    def validate_registration_method_data(cls, v, values):
        """Validate that required fields are present for registration method."""
        if v == RegistrationMethod.EMAIL_ONLY and not values.get('email'):
            raise ValueError('Email is required for email-only registration')
        elif v == RegistrationMethod.PHONE_ONLY and not values.get('phone'):
            raise ValueError('Phone is required for phone-only registration')
        elif v == RegistrationMethod.EMAIL_AND_PHONE:
            if not values.get('email') or not values.get('phone'):
                raise ValueError('Both email and phone are required for combined registration')
        return v

class EnhancedRegistrationResponse(BaseModel):
    """Enhanced registration response with fraud prevention details."""
    success: bool = Field(description="Whether registration was successful")
    message: str = Field(description="Response message")
    
    # Registration result
    user_id: Optional[int] = Field(default=None, description="User ID if registration successful")
    registration_id: Optional[str] = Field(default=None, description="Registration attempt ID")
    
    # Verification requirements
    requires_email_verification: bool = Field(description="Email verification required")
    requires_phone_verification: bool = Field(description="Phone verification required")
    requires_captcha: bool = Field(description="CAPTCHA verification required")
    requires_manual_review: bool = Field(description="Manual review required")
    
    # Risk assessment
    risk_level: str = Field(description="Risk level (low, medium, high)")
    risk_score: Optional[float] = Field(default=None, description="Risk score (0-1)")
    fraud_prevention_action: str = Field(description="Action taken by fraud prevention")
    
    # Credits and verification
    assigned_credits: Optional[int] = Field(default=None, description="Credits assigned")
    verification_level: str = Field(description="Required verification level")
    
    # Next steps
    next_steps: List[str] = Field(description="What user should do next")
    verification_urls: Dict[str, str] = Field(default_factory=dict, description="Verification URLs")
    
    # Error details (if registration failed)
    error_code: Optional[str] = Field(default=None, description="Error code if failed")
    blocked_reason: Optional[str] = Field(default=None, description="Reason if blocked")
    retry_after_seconds: Optional[int] = Field(default=None, description="Retry cooldown period")
    
    # Rate limiting info
    rate_limit_info: Optional[Dict[str, Any]] = Field(default=None, description="Rate limiting information")
    
    # Metadata
    registration_timestamp: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(default=None, description="When verification expires")

class FraudPreventionValidationRequest(BaseModel):
    """Request for fraud prevention validation before registration."""
    ip_address: str = Field(description="User IP address")
    user_agent: str = Field(description="User agent string")
    platform: str = Field(description="Registration platform")
    
    # Optional pre-validation data
    email: Optional[str] = Field(default=None, description="Email to pre-validate")
    phone: Optional[str] = Field(default=None, description="Phone to pre-validate")
    
    # Device information
    device_fingerprint: Optional[Dict[str, Any]] = Field(default=None, description="Device fingerprint")
    
    # CAPTCHA if already solved
    captcha_response: Optional[str] = Field(default=None, description="CAPTCHA response")

class FraudPreventionValidationResponse(BaseModel):
    """Response for fraud prevention pre-validation."""
    allowed: bool = Field(description="Whether registration is allowed")
    risk_level: str = Field(description="Risk level assessment")
    
    # Requirements
    captcha_required: bool = Field(description="CAPTCHA verification required")
    phone_verification_required: bool = Field(description="Phone verification required")
    email_verification_required: bool = Field(description="Email verification required")
    
    # Rate limiting
    rate_limited: bool = Field(description="Whether rate limited")
    retry_after_seconds: Optional[int] = Field(default=None, description="Retry cooldown")
    
    # CAPTCHA configuration
    captcha_config: Optional[Dict[str, Any]] = Field(default=None, description="CAPTCHA configuration")
    
    # Messages
    message: str = Field(description="Validation message")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    
    # Credits preview
    expected_credits: int = Field(description="Expected credits if registration succeeds")

class RegistrationVerificationRequest(BaseModel):
    """Request to verify registration (email/phone/captcha)."""
    registration_id: str = Field(description="Registration attempt ID")
    verification_type: str = Field(description="Type of verification (email, phone, captcha)")
    verification_code: Optional[str] = Field(default=None, description="Verification code")
    captcha_response: Optional[str] = Field(default=None, description="CAPTCHA response")
    
    # Context
    ip_address: Optional[str] = Field(default=None, description="User IP address")
    user_agent: Optional[str] = Field(default=None, description="User agent")

class RegistrationVerificationResponse(BaseModel):
    """Response for registration verification."""
    success: bool = Field(description="Whether verification was successful")
    message: str = Field(description="Verification result message")
    
    # Verification status
    verification_complete: bool = Field(description="Whether all verifications are complete")
    remaining_verifications: List[str] = Field(description="Remaining verification steps")
    
    # Account status
    account_activated: bool = Field(description="Whether account is now activated")
    user_id: Optional[int] = Field(default=None, description="User ID if account activated")
    
    # Authentication tokens (if account activated)
    access_token: Optional[str] = Field(default=None, description="Access token")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    token_expires_in: Optional[int] = Field(default=None, description="Token expiry in seconds")
    
    # Next steps
    next_steps: List[str] = Field(description="What user should do next")
    redirect_url: Optional[str] = Field(default=None, description="Where to redirect user")

class SecurityChallengeRequest(BaseModel):
    """Request for additional security challenge."""
    challenge_type: str = Field(description="Type of challenge (captcha, sms, email)")
    user_identifier: str = Field(description="User identifier (email, phone, user_id)")
    reason: str = Field(description="Reason for challenge")
    
    # Context
    ip_address: str = Field(description="User IP address")
    user_agent: str = Field(description="User agent")
    session_id: Optional[str] = Field(default=None, description="Session ID")

class SecurityChallengeResponse(BaseModel):
    """Response for security challenge."""
    success: bool = Field(description="Whether challenge was initiated")
    challenge_id: str = Field(description="Challenge identifier")
    challenge_type: str = Field(description="Type of challenge")
    
    # Challenge details
    expires_in_seconds: int = Field(description="Challenge expiry time")
    max_attempts: int = Field(description="Maximum attempts allowed")
    
    # Instructions
    instructions: str = Field(description="Instructions for user")
    next_steps: List[str] = Field(description="What user should do next") 