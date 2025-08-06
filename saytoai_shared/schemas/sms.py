"""
SMS verification and phone authentication schemas for SayToAI ecosystem.
Supports dual delivery methods: Telegram bot and external SMS service.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..constants import (
    RegistrationMethod,
    SMSDeliveryMethod,
    PhoneVerificationStatus,
    SMSCodePurpose,
    SMS_CODE_LENGTH,
    SMSDeliveryStatus
)
from ..utils import validate_phone_number, normalize_phone_for_comparison

class PhoneRegistrationRequest(BaseModel):
    """Request for phone number registration with SMS verification."""
    phone: str = Field(description="Phone number with country code")
    password: Optional[str] = Field(default=None, min_length=8, max_length=128, description="Password (if email+phone registration)")
    email: Optional[str] = Field(default=None, description="Email address (if email+phone registration)")
    registration_method: RegistrationMethod = Field(default=RegistrationMethod.PHONE_ONLY, description="Registration method")
    language: str = Field(default="english", description="Preferred language")
    terms_accepted: bool = Field(description="Terms and conditions acceptance")
    marketing_consent: bool = Field(default=False, description="Marketing SMS consent")
    
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
    
    @validator('terms_accepted')
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v

class SMSVerificationRequest(BaseModel):
    """Request to send SMS verification code."""
    phone: str = Field(description="Phone number to send SMS to")
    purpose: SMSCodePurpose = Field(default=SMSCodePurpose.REGISTRATION, description="Purpose of SMS code")
    language: str = Field(default="english", description="SMS language")
    
    # Optional context for delivery method determination
    user_id: Optional[int] = Field(default=None, description="User ID if known")
    check_telegram_existence: bool = Field(default=True, description="Check if user exists in Telegram")
    
    @validator('phone')
    def validate_phone_format(cls, v):
        validation_result = validate_phone_number(v)
        if not validation_result["is_valid"]:
            raise ValueError(validation_result["message"])
        return validation_result["formatted_phone"]

class SMSCodeVerificationRequest(BaseModel):
    """Request to verify SMS code."""
    phone: str = Field(description="Phone number")
    code: str = Field(min_length=SMS_CODE_LENGTH, max_length=SMS_CODE_LENGTH, description="SMS verification code")
    purpose: SMSCodePurpose = Field(default=SMSCodePurpose.REGISTRATION, description="Purpose of verification")
    
    @validator('phone')
    def validate_phone_format(cls, v):
        validation_result = validate_phone_number(v)
        if not validation_result["is_valid"]:
            raise ValueError(validation_result["message"])
        return validation_result["formatted_phone"]
    
    @validator('code')
    def validate_code_format(cls, v):
        if not v.isdigit():
            raise ValueError('SMS code must contain only digits')
        return v

class SMSVerificationCode(BaseModel):
    """SMS verification code model."""
    id: Optional[int] = Field(default=None, description="Code ID")
    phone: str = Field(description="Phone number")
    normalized_phone: str = Field(description="Normalized phone for comparison")
    code: str = Field(description="Verification code")
    purpose: SMSCodePurpose = Field(description="Code purpose")
    
    # Delivery information
    delivery_method: SMSDeliveryMethod = Field(description="How SMS was delivered")
    delivery_provider: str = Field(description="SMS provider used")
    delivery_cost: float = Field(ge=0.0, description="Cost of SMS delivery")
    delivery_currency: str = Field(description="Currency of cost")
    
    # Status and timing
    status: PhoneVerificationStatus = Field(default=PhoneVerificationStatus.PENDING, description="Verification status")
    created_at: datetime = Field(default_factory=datetime.now, description="When code was created")
    expires_at: datetime = Field(description="When code expires")
    verified_at: Optional[datetime] = Field(default=None, description="When code was verified")
    
    # Attempt tracking
    verification_attempts: int = Field(default=0, ge=0, description="Number of verification attempts")
    max_attempts: int = Field(default=3, description="Maximum verification attempts")
    
    # Metadata
    user_id: Optional[int] = Field(default=None, description="Associated user ID")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    ip_address: Optional[str] = Field(default=None, description="IP address of request")
    user_agent: Optional[str] = Field(default=None, description="User agent")
    
    @validator('normalized_phone', pre=True, always=True)
    def set_normalized_phone(cls, v, values):
        if 'phone' in values:
            return normalize_phone_for_comparison(values['phone'])
        return v

class SMSDeliveryInfo(BaseModel):
    """Information about SMS delivery method and cost."""
    method: SMSDeliveryMethod = Field(description="Delivery method")
    provider: str = Field(description="SMS provider")
    cost: float = Field(ge=0.0, description="Cost per SMS")
    currency: str = Field(description="Currency")
    estimated_delivery_time: str = Field(description="Estimated delivery time")
    reliability: str = Field(description="Reliability level")
    reason: str = Field(description="Reason for choosing this method")
    
    # Additional details
    supports_delivery_receipt: bool = Field(default=False, description="Whether delivery receipts are supported")
    character_limit: int = Field(default=160, description="SMS character limit")
    unicode_support: bool = Field(default=True, description="Unicode character support")

class SMSVerificationResponse(BaseModel):
    """Response for SMS verification request."""
    success: bool = Field(description="Whether SMS was sent successfully")
    message: str = Field(description="Response message")
    
    # SMS details
    phone: str = Field(description="Phone number SMS was sent to")
    delivery_info: SMSDeliveryInfo = Field(description="Delivery method information")
    
    # Timing information
    code_expires_in_minutes: int = Field(description="Code expiry time in minutes")
    can_resend_in_seconds: int = Field(description="Cooldown before next SMS")
    
    # Rate limiting info
    attempts_remaining: int = Field(description="SMS attempts remaining this hour")
    daily_limit_remaining: int = Field(description="Daily SMS limit remaining")
    
    # Verification details
    verification_id: Optional[str] = Field(default=None, description="Verification session ID")
    next_steps: List[str] = Field(description="What user should do next")

class SMSCodeVerificationResponse(BaseModel):
    """Response for SMS code verification."""
    success: bool = Field(description="Whether code verification was successful")
    message: str = Field(description="Verification result message")
    
    # Verification details
    phone: str = Field(description="Verified phone number")
    verification_status: PhoneVerificationStatus = Field(description="Final verification status")
    
    # User information (if verification successful)
    user_id: Optional[int] = Field(default=None, description="User ID if registration completed")
    account_created: bool = Field(default=False, description="Whether new account was created")
    
    # Next steps
    next_steps: List[str] = Field(description="What user should do next")
    redirect_url: Optional[str] = Field(default=None, description="Where to redirect user")
    
    # Error details (if verification failed)
    error_code: Optional[str] = Field(default=None, description="Error code if failed")
    attempts_remaining: int = Field(description="Verification attempts remaining")
    can_request_new_code: bool = Field(description="Whether user can request new code")

class PhoneVerificationSession(BaseModel):
    """Phone verification session tracking."""
    id: Optional[int] = Field(default=None)
    session_id: str = Field(description="Unique session identifier")
    phone: str = Field(description="Phone number being verified")
    normalized_phone: str = Field(description="Normalized phone number")
    
    # Session details
    purpose: SMSCodePurpose = Field(description="Verification purpose")
    registration_method: RegistrationMethod = Field(description="Registration method")
    current_step: str = Field(description="Current verification step")
    
    # Status tracking
    status: PhoneVerificationStatus = Field(description="Session status")
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(default=None)
    expires_at: datetime = Field(description="Session expiry time")
    
    # SMS tracking
    sms_codes_sent: int = Field(default=0, description="Number of SMS codes sent")
    last_sms_sent_at: Optional[datetime] = Field(default=None)
    verification_attempts: int = Field(default=0, description="Total verification attempts")
    
    # User context
    user_id: Optional[int] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    device_fingerprint: Optional[str] = Field(default=None)
    
    # Additional data
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session data")

class SMSUsageStats(BaseModel):
    """SMS usage statistics and analytics."""
    phone: str = Field(description="Phone number")
    
    # Usage counts
    total_sms_sent: int = Field(ge=0, description="Total SMS messages sent")
    successful_verifications: int = Field(ge=0, description="Successful verifications")
    failed_verifications: int = Field(ge=0, description="Failed verifications")
    
    # Cost tracking
    total_cost: float = Field(ge=0.0, description="Total SMS cost")
    cost_currency: str = Field(description="Cost currency")
    
    # Delivery method breakdown
    telegram_deliveries: int = Field(ge=0, description="SMS sent via Telegram")
    external_deliveries: int = Field(ge=0, description="SMS sent via external service")
    
    # Time tracking
    first_sms_sent: Optional[datetime] = Field(default=None)
    last_sms_sent: Optional[datetime] = Field(default=None)
    
    # Quality metrics
    average_verification_time_seconds: Optional[float] = Field(default=None)
    delivery_success_rate: float = Field(ge=0.0, le=1.0, description="SMS delivery success rate")

class SMSProviderConfig(BaseModel):
    """SMS provider configuration."""
    provider_name: str = Field(description="Provider name")
    provider_type: SMSDeliveryMethod = Field(description="Provider type")
    
    # Configuration
    is_active: bool = Field(default=True, description="Whether provider is active")
    priority: int = Field(default=1, description="Provider priority (1=highest)")
    
    # Limits and costs
    cost_per_sms: float = Field(ge=0.0, description="Cost per SMS")
    currency: str = Field(description="Cost currency")
    daily_limit: int = Field(ge=0, description="Daily SMS limit")
    rate_limit_per_minute: int = Field(ge=0, description="Rate limit per minute")
    
    # Capabilities
    supports_unicode: bool = Field(default=True)
    supports_delivery_receipts: bool = Field(default=False)
    max_message_length: int = Field(default=160)
    
    # Geographic support
    supported_countries: List[str] = Field(description="Supported country codes")
    
    # API configuration
    api_endpoint: Optional[str] = Field(default=None)
    api_key: Optional[str] = Field(default=None)
    api_secret: Optional[str] = Field(default=None)
    
    # Reliability metrics
    success_rate: float = Field(ge=0.0, le=1.0, description="Historical success rate")
    average_delivery_time_seconds: float = Field(ge=0.0, description="Average delivery time")

# Batch operations
class BulkSMSRequest(BaseModel):
    """Request for sending SMS to multiple phone numbers."""
    phones: List[str] = Field(description="List of phone numbers")
    message_template: str = Field(description="SMS message template")
    purpose: SMSCodePurpose = Field(description="SMS purpose")
    
    # Delivery preferences
    preferred_method: Optional[SMSDeliveryMethod] = Field(default=None)
    check_telegram_existence: bool = Field(default=True)
    
    # Scheduling
    send_immediately: bool = Field(default=True)
    scheduled_at: Optional[datetime] = Field(default=None)
    
    @validator('phones')
    def validate_phone_list(cls, v):
        if len(v) == 0:
            raise ValueError('At least one phone number is required')
        if len(v) > 100:  # Reasonable batch limit
            raise ValueError('Maximum 100 phone numbers per batch')
        
        validated_phones = []
        for phone in v:
            validation_result = validate_phone_number(phone)
            if not validation_result["is_valid"]:
                raise ValueError(f'Invalid phone number: {phone} - {validation_result["message"]}')
            validated_phones.append(validation_result["formatted_phone"])
        
        return validated_phones

class BulkSMSResponse(BaseModel):
    """Response for bulk SMS sending."""
    total_phones: int = Field(description="Total phone numbers processed")
    successful_sends: int = Field(description="Successfully sent SMS count")
    failed_sends: int = Field(description="Failed SMS count")
    
    # Cost breakdown
    total_cost: float = Field(description="Total cost")
    cost_currency: str = Field(description="Cost currency")
    telegram_sends: int = Field(description="SMS sent via Telegram (free)")
    external_sends: int = Field(description="SMS sent via external service (paid)")
    
    # Detailed results
    successful_phones: List[str] = Field(description="Successfully processed phones")
    failed_phones: List[Dict[str, str]] = Field(description="Failed phones with error messages")
    
    # Timing
    processing_time_seconds: float = Field(description="Total processing time")
    estimated_delivery_time: str = Field(description="Estimated delivery time")

# ===== SMS VERIFICATION WORKFLOW SCHEMAS =====

class SMSVerificationWorkflowRequest(BaseModel):
    """Request to start SMS verification workflow."""
    phone_number: str = Field(..., description="Phone number to verify")
    user_id: Optional[str] = Field(None, description="User ID if available")
    purpose: SMSCodePurpose = Field(SMSCodePurpose.REGISTRATION, description="Purpose of verification")
    preferred_language: Optional[str] = Field("en", description="Preferred language for SMS")
    retry_attempt: int = Field(0, description="Current retry attempt number")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+1234567890",
                "user_id": "user_123",
                "purpose": "registration",
                "preferred_language": "en",
                "retry_attempt": 0
            }
        }

class SMSVerificationWorkflowResponse(BaseModel):
    """Response from SMS verification workflow."""
    workflow_id: str = Field(..., description="Unique workflow identifier")
    status: str = Field(..., description="Current workflow status")
    phone_number: str = Field(..., description="Phone number being verified")
    delivery_method: SMSDeliveryMethod = Field(..., description="SMS delivery method used")
    delivery_status: SMSDeliveryStatus = Field(..., description="SMS delivery status")
    message: str = Field(..., description="Status message for user")
    next_action: Optional[str] = Field(None, description="Next action user should take")
    retry_available: bool = Field(False, description="Whether retry is available")
    retry_cooldown_seconds: Optional[int] = Field(None, description="Seconds until retry is available")
    admin_contact_required: bool = Field(False, description="Whether admin contact is required")
    expires_at: Optional[datetime] = Field(None, description="When the workflow expires")
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_abc123",
                "status": "pending",
                "phone_number": "+1234567890",
                "delivery_method": "external_sms",
                "delivery_status": "sent",
                "message": "SMS sent successfully. Please enter the verification code.",
                "next_action": "enter_code",
                "retry_available": True,
                "retry_cooldown_seconds": 120,
                "admin_contact_required": False,
                "expires_at": "2024-01-01T12:05:00Z"
            }
        }

class SMSVerificationConfirmationRequest(BaseModel):
    """Request to confirm SMS verification after failure."""
    workflow_id: str = Field(..., description="Workflow identifier")
    user_confirmed: bool = Field(..., description="Whether user wants to retry")
    alternative_contact: Optional[str] = Field(None, description="Alternative contact method if provided")
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_abc123",
                "user_confirmed": True,
                "alternative_contact": "user@example.com"
            }
        }

class SMSVerificationRetryRequest(BaseModel):
    """Request to retry SMS verification."""
    workflow_id: str = Field(..., description="Workflow identifier")
    phone_number: Optional[str] = Field(None, description="Updated phone number if changed")
    force_delivery_method: Optional[SMSDeliveryMethod] = Field(None, description="Force specific delivery method")
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_abc123",
                "phone_number": "+1234567890",
                "force_delivery_method": "telegram_bot"
            }
        }

class AdminVerificationRequest(BaseModel):
    """Request for admin to manually verify phone number."""
    workflow_id: str = Field(..., description="Workflow identifier")
    phone_number: str = Field(..., description="Phone number to verify")
    user_id: Optional[str] = Field(None, description="User ID if available")
    admin_id: str = Field(..., description="Admin performing the verification")
    action: str = Field(..., description="Admin action to take")
    notes: Optional[str] = Field(None, description="Admin notes")
    verification_method: Optional[str] = Field(None, description="Method used for verification")
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_abc123",
                "phone_number": "+1234567890",
                "user_id": "user_123",
                "admin_id": "admin_456",
                "action": "manual_verify",
                "notes": "Verified via phone call",
                "verification_method": "phone_call"
            }
        }

class AdminVerificationResponse(BaseModel):
    """Response from admin verification."""
    workflow_id: str = Field(..., description="Workflow identifier")
    status: str = Field(..., description="New workflow status")
    action_taken: str = Field(..., description="Action that was taken")
    verified: bool = Field(..., description="Whether phone was verified")
    message: str = Field(..., description="Result message")
    admin_id: str = Field(..., description="Admin who performed the action")
    timestamp: datetime = Field(..., description="When action was performed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_abc123",
                "status": "admin_verified",
                "action_taken": "manual_verify",
                "verified": True,
                "message": "Phone number manually verified by admin",
                "admin_id": "admin_456",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }

class SMSWorkflowStatusResponse(BaseModel):
    """Response with current workflow status."""
    workflow_id: str = Field(..., description="Workflow identifier")
    status: str = Field(..., description="Current status")
    phone_number: str = Field(..., description="Phone number")
    created_at: datetime = Field(..., description="When workflow was created")
    updated_at: datetime = Field(..., description="Last update time")
    expires_at: Optional[datetime] = Field(None, description="Expiration time")
    attempt_count: int = Field(..., description="Number of attempts made")
    max_attempts: int = Field(..., description="Maximum attempts allowed")
    last_error: Optional[str] = Field(None, description="Last error message")
    delivery_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of delivery attempts")
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "wf_abc123",
                "status": "awaiting_confirmation",
                "phone_number": "+1234567890",
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:02:00Z",
                "expires_at": "2024-01-01T12:07:00Z",
                "attempt_count": 1,
                "max_attempts": 2,
                "last_error": "SMS delivery failed",
                "delivery_history": [
                    {
                        "attempt": 1,
                        "method": "external_sms",
                        "status": "failed",
                        "timestamp": "2024-01-01T12:02:00Z",
                        "error": "Invalid phone number"
                    }
                ]
            }
        } 