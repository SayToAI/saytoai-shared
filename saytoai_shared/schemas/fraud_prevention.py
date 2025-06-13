"""
Fraud Prevention and Anti-Abuse schemas for SayToAI ecosystem.
Implements comprehensive validation, risk scoring, and abuse detection.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..constants import (
    AccountVerificationLevel,
    FraudDetectionAction
)

class DeviceFingerprint(BaseModel):
    """Device fingerprinting data for fraud detection."""
    fingerprint_id: str = Field(description="Unique device fingerprint hash")
    
    # Required fields
    user_agent: str = Field(description="User agent string")
    screen_resolution: str = Field(description="Screen resolution (e.g., 1920x1080)")
    timezone: str = Field(description="User timezone")
    language: str = Field(description="Browser language")
    platform: str = Field(description="Operating system platform")
    
    # Optional advanced fingerprinting
    canvas_fingerprint: Optional[str] = Field(default=None, description="Canvas fingerprint hash")
    webgl_fingerprint: Optional[str] = Field(default=None, description="WebGL fingerprint hash")
    audio_fingerprint: Optional[str] = Field(default=None, description="Audio context fingerprint")
    font_list: Optional[List[str]] = Field(default=None, description="Available fonts list")
    plugins_list: Optional[List[str]] = Field(default=None, description="Browser plugins list")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    account_count: int = Field(default=0, description="Number of accounts using this fingerprint")
    is_suspicious: bool = Field(default=False, description="Whether fingerprint is flagged as suspicious")

class IPAnalysis(BaseModel):
    """IP address analysis and risk assessment."""
    ip_address: str = Field(description="IP address")
    
    # Geolocation data
    country_code: Optional[str] = Field(default=None, description="Country code (ISO 3166-1 alpha-2)")
    country_name: Optional[str] = Field(default=None, description="Country name")
    city: Optional[str] = Field(default=None, description="City name")
    region: Optional[str] = Field(default=None, description="Region/state")
    latitude: Optional[float] = Field(default=None, description="Latitude")
    longitude: Optional[float] = Field(default=None, description="Longitude")
    
    # Network information
    isp: Optional[str] = Field(default=None, description="Internet Service Provider")
    organization: Optional[str] = Field(default=None, description="Organization")
    asn: Optional[int] = Field(default=None, description="Autonomous System Number")
    
    # Risk factors
    is_vpn: bool = Field(default=False, description="Whether IP is from VPN")
    is_proxy: bool = Field(default=False, description="Whether IP is from proxy")
    is_tor: bool = Field(default=False, description="Whether IP is from Tor network")
    is_datacenter: bool = Field(default=False, description="Whether IP is from datacenter")
    is_suspicious: bool = Field(default=False, description="Overall suspicion flag")
    is_blacklisted: bool = Field(default=False, description="Whether IP is blacklisted")
    
    # Risk scoring
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="IP risk score (0-1)")
    threat_types: List[str] = Field(default_factory=list, description="Detected threat types")
    
    # Usage statistics
    registration_attempts_today: int = Field(default=0, description="Registration attempts today")
    successful_registrations_today: int = Field(default=0, description="Successful registrations today")
    last_registration_attempt: Optional[datetime] = Field(default=None)

class CaptchaValidation(BaseModel):
    """CAPTCHA validation result."""
    provider: str = Field(description="CAPTCHA provider (recaptcha_v2, recaptcha_v3, hcaptcha)")
    response_token: str = Field(description="CAPTCHA response token")
    
    # Validation result
    success: bool = Field(description="Whether CAPTCHA validation passed")
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="CAPTCHA score (for v3)")
    action: Optional[str] = Field(default=None, description="Action that triggered CAPTCHA")
    challenge_ts: Optional[datetime] = Field(default=None, description="Challenge timestamp")
    hostname: Optional[str] = Field(default=None, description="Hostname where CAPTCHA was solved")
    
    # Error information
    error_codes: List[str] = Field(default_factory=list, description="Error codes if validation failed")
    
    # Metadata
    validated_at: datetime = Field(default_factory=datetime.now)
    ip_address: Optional[str] = Field(default=None, description="IP address of user")

class RiskAssessment(BaseModel):
    """Comprehensive risk assessment for user registration."""
    assessment_id: str = Field(description="Unique assessment identifier")
    
    # Overall risk
    risk_score: float = Field(ge=0.0, le=1.0, description="Overall risk score (0-1)")
    risk_level: str = Field(description="Risk level (low, medium, high)")
    
    # Risk factors
    risk_factors: List[str] = Field(description="List of detected risk factors")
    risk_factor_weights: Dict[str, float] = Field(description="Weight of each risk factor")
    
    # Recommendations
    should_block: bool = Field(description="Whether registration should be blocked")
    requires_manual_review: bool = Field(description="Whether manual review is required")
    requires_additional_verification: bool = Field(description="Whether additional verification is needed")
    
    # Verification requirements
    email_verification_required: bool = Field(description="Email verification required")
    phone_verification_required: bool = Field(description="Phone verification required")
    captcha_required: bool = Field(description="CAPTCHA verification required")
    
    # Metadata
    assessed_at: datetime = Field(default_factory=datetime.now)
    assessment_version: str = Field(default="1.0", description="Risk assessment algorithm version")

class RegistrationAttempt(BaseModel):
    """Registration attempt tracking for fraud detection."""
    attempt_id: str = Field(description="Unique attempt identifier")
    
    # User data
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    name: Optional[str] = Field(default=None, description="User name")
    
    # Platform and timing
    platform: str = Field(description="Registration platform (web, telegram)")
    form_start_time: Optional[datetime] = Field(default=None, description="When user started form")
    form_submit_time: datetime = Field(default_factory=datetime.now, description="When form was submitted")
    registration_time_seconds: Optional[float] = Field(default=None, description="Time taken to fill form")
    
    # Device and network
    ip_address: str = Field(description="User IP address")
    user_agent: str = Field(description="User agent string")
    device_fingerprint: Optional[DeviceFingerprint] = Field(default=None)
    ip_analysis: Optional[IPAnalysis] = Field(default=None)
    
    # Verification data
    captcha_validation: Optional[CaptchaValidation] = Field(default=None)
    
    # Risk assessment
    risk_assessment: Optional[RiskAssessment] = Field(default=None)
    
    # Result
    status: str = Field(description="Attempt status (pending, approved, rejected, review)")
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection")
    assigned_credits: Optional[int] = Field(default=None, description="Credits assigned if approved")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class FraudPreventionReport(BaseModel):
    """Comprehensive fraud prevention report."""
    report_id: str = Field(description="Unique report identifier")
    registration_attempt: RegistrationAttempt = Field(description="Registration attempt data")
    
    # Analysis results
    risk_assessment: RiskAssessment = Field(description="Risk assessment results")
    ip_analysis: IPAnalysis = Field(description="IP analysis results")
    device_analysis: Optional[Dict[str, Any]] = Field(default=None, description="Device analysis results")
    
    # Rate limiting
    ip_rate_limit_status: Dict[str, Any] = Field(description="IP rate limiting status")
    account_limits_status: Dict[str, Any] = Field(description="Account creation limits status")
    
    # Timing analysis
    timing_validation: Optional[Dict[str, Any]] = Field(default=None, description="Registration timing analysis")
    
    # Verification requirements
    verification_requirements: Dict[str, bool] = Field(description="Required verification steps")
    
    # Recommended action
    recommended_action: FraudDetectionAction = Field(description="Recommended action to take")
    action_reason: str = Field(description="Reason for recommended action")
    
    # Credits and platform
    platform_credits: int = Field(description="Credits to assign based on platform")
    verification_level: AccountVerificationLevel = Field(description="Required verification level")
    
    # Flags
    requires_manual_review: bool = Field(description="Whether manual review is needed")
    additional_checks_needed: bool = Field(description="Whether additional checks are needed")
    is_high_risk: bool = Field(description="Whether this is a high-risk registration")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.now)
    report_version: str = Field(default="1.0", description="Report format version")

class IPRateLimit(BaseModel):
    """IP address rate limiting tracking."""
    ip_address: str = Field(description="IP address")
    action_type: str = Field(description="Type of action (registration, sms_request, etc.)")
    time_window: str = Field(description="Time window (minute, hour, day)")
    
    # Limits and counts
    current_count: int = Field(ge=0, description="Current count in time window")
    limit: int = Field(ge=0, description="Maximum allowed in time window")
    allowed: bool = Field(description="Whether action is allowed")
    
    # Timing
    window_start: datetime = Field(description="Start of current time window")
    window_end: datetime = Field(description="End of current time window")
    reset_time: Optional[datetime] = Field(default=None, description="When limit resets")
    retry_after_seconds: int = Field(default=0, description="Seconds to wait before retry")
    
    # History
    total_attempts: int = Field(default=0, description="Total attempts ever")
    successful_attempts: int = Field(default=0, description="Successful attempts")
    blocked_attempts: int = Field(default=0, description="Blocked attempts")
    
    # Metadata
    first_attempt: Optional[datetime] = Field(default=None, description="First attempt timestamp")
    last_attempt: datetime = Field(default_factory=datetime.now, description="Last attempt timestamp")

class SuspiciousActivity(BaseModel):
    """Suspicious activity detection and logging."""
    activity_id: str = Field(description="Unique activity identifier")
    activity_type: str = Field(description="Type of suspicious activity")
    severity: str = Field(description="Severity level (low, medium, high, critical)")
    
    # Activity details
    description: str = Field(description="Description of suspicious activity")
    detected_patterns: List[str] = Field(description="Patterns that triggered detection")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in detection")
    
    # Associated data
    ip_address: Optional[str] = Field(default=None, description="Associated IP address")
    user_id: Optional[int] = Field(default=None, description="Associated user ID")
    device_fingerprint: Optional[str] = Field(default=None, description="Associated device fingerprint")
    
    # Context
    request_data: Dict[str, Any] = Field(description="Request data that triggered detection")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    referrer: Optional[str] = Field(default=None, description="HTTP referrer")
    
    # Actions taken
    actions_taken: List[str] = Field(description="Actions taken in response")
    blocked: bool = Field(default=False, description="Whether request was blocked")
    flagged_for_review: bool = Field(default=False, description="Whether flagged for manual review")
    
    # Metadata
    detected_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = Field(default=None, description="When activity was resolved")
    resolved_by: Optional[str] = Field(default=None, description="Who resolved the activity")

class AccountVerificationStatus(BaseModel):
    """Account verification status tracking."""
    user_id: int = Field(description="User ID")
    verification_level: AccountVerificationLevel = Field(description="Current verification level")
    
    # Verification status
    email_verified: bool = Field(default=False, description="Email verification status")
    phone_verified: bool = Field(default=False, description="Phone verification status")
    identity_verified: bool = Field(default=False, description="Identity verification status")
    
    # Verification timestamps
    email_verified_at: Optional[datetime] = Field(default=None)
    phone_verified_at: Optional[datetime] = Field(default=None)
    identity_verified_at: Optional[datetime] = Field(default=None)
    
    # Risk assessment
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Current risk score")
    risk_level: str = Field(default="low", description="Current risk level")
    
    # Flags
    requires_manual_review: bool = Field(default=False, description="Requires manual review")
    is_suspended: bool = Field(default=False, description="Account is suspended")
    is_flagged: bool = Field(default=False, description="Account is flagged for review")
    
    # Credits and limits
    assigned_credits: int = Field(default=0, description="Credits assigned to account")
    credit_source: str = Field(default="platform", description="Source of credits")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_risk_assessment: Optional[datetime] = Field(default=None)

class FraudPreventionConfig(BaseModel):
    """Fraud prevention system configuration."""
    
    # Risk scoring
    risk_scoring_enabled: bool = Field(default=True, description="Enable risk scoring")
    risk_thresholds: Dict[str, float] = Field(description="Risk level thresholds")
    
    # Rate limiting
    ip_rate_limiting_enabled: bool = Field(default=True, description="Enable IP rate limiting")
    rate_limits: Dict[str, int] = Field(description="Rate limit configurations")
    
    # CAPTCHA
    captcha_enabled: bool = Field(default=True, description="Enable CAPTCHA verification")
    captcha_config: Dict[str, Any] = Field(description="CAPTCHA configuration")
    
    # Device fingerprinting
    device_fingerprinting_enabled: bool = Field(default=True, description="Enable device fingerprinting")
    fingerprint_required: bool = Field(default=True, description="Require device fingerprint")
    
    # Phone validation
    enhanced_phone_validation: bool = Field(default=True, description="Enable enhanced phone validation")
    block_voip_numbers: bool = Field(default=True, description="Block VoIP numbers")
    require_mobile_only: bool = Field(default=True, description="Require mobile numbers only")
    
    # Email validation
    enhanced_email_validation: bool = Field(default=True, description="Enable enhanced email validation")
    block_disposable_emails: bool = Field(default=True, description="Block disposable email addresses")
    
    # Geolocation
    ip_geolocation_enabled: bool = Field(default=True, description="Enable IP geolocation")
    block_vpn_proxy: bool = Field(default=False, description="Block VPN/proxy connections")
    
    # Monitoring
    suspicious_activity_monitoring: bool = Field(default=True, description="Monitor suspicious activity")
    auto_cleanup_enabled: bool = Field(default=True, description="Auto cleanup fake accounts")
    
    # Credits
    platform_credit_allocation: Dict[str, int] = Field(description="Credits per platform")
    
    # Metadata
    config_version: str = Field(default="1.0", description="Configuration version")
    last_updated: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[str] = Field(default=None, description="Who updated the config") 