"""
User-related Pydantic schemas for SayToAI ecosystem.
Updated with enums, shared mixins, and password authentication support.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..constants import (
    SubscriptionType, 
    SubscriptionStatus,
    UserRole,
    AuthMethod,
    DEFAULT_LANGUAGE,
    DEFAULT_AUDIO_LANGUAGE,
    DEFAULT_OUTPUT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    AUDIO_LANGUAGES,
    USER_ROLES_LIST
)

class LanguageValidatorMixin(BaseModel):
    """Shared language validation logic."""
    
    @validator('language', 'output_language', allow_reuse=True, check_fields=False)
    def validate_language_fields(cls, v):
        if v is not None and v not in SUPPORTED_LANGUAGES:
            raise ValueError(f'Language must be one of: {SUPPORTED_LANGUAGES}')
        return v
    
    @validator('audio_language', allow_reuse=True, check_fields=False)
    def validate_audio_language(cls, v):
        if v is not None and v not in AUDIO_LANGUAGES:
            raise ValueError(f'Audio language must be one of: {AUDIO_LANGUAGES}')
        return v

class RoleValidatorMixin(BaseModel):
    """Shared role validation logic."""
    
    @validator('role', allow_reuse=True, check_fields=False)
    def validate_role(cls, v):
        if v is not None and v not in USER_ROLES_LIST:
            raise ValueError(f'Role must be one of: {USER_ROLES_LIST}')
        return v

class UserPreferences(LanguageValidatorMixin):
    """User preferences and settings."""
    language: Optional[str] = Field(default=None, description="User interface language")
    role: Optional[UserRole] = Field(default=None, description="User role preference")
    audio_language: str = Field(default=DEFAULT_AUDIO_LANGUAGE, description="Audio input language")
    output_language: str = Field(default=DEFAULT_OUTPUT_LANGUAGE, description="Output text language")
    
    # New preference fields
    notifications_enabled: bool = Field(default=True, description="Enable notifications")
    dark_mode: bool = Field(default=False, description="Enable dark mode")
    auto_transcribe: bool = Field(default=True, description="Auto-transcribe audio messages")

class UserCredits(BaseModel):
    """User credit account information."""
    remaining: int = Field(ge=0, description="Remaining credits")
    total_used: int = Field(ge=0, description="Total credits used")
    last_used_at: Optional[datetime] = Field(default=None, description="Last credit usage timestamp")
    
    # Credit tracking
    daily_usage: int = Field(default=0, ge=0, description="Credits used today")
    monthly_usage: int = Field(default=0, ge=0, description="Credits used this month")
    
class UserSubscription(BaseModel):
    """User subscription information."""
    subscription_type: SubscriptionType = Field(default=SubscriptionType.FREE_TRIAL)
    status: SubscriptionStatus = Field(default=SubscriptionStatus.ACTIVE)
    expires_at: Optional[datetime] = Field(default=None, description="Subscription expiry date")
    created_at: Optional[datetime] = Field(default=None, description="Subscription creation date")
    
    # Subscription features
    monthly_credit_limit: int = Field(default=50, ge=0, description="Monthly credit allowance")
    features: List[str] = Field(default_factory=list, description="Enabled features")

class UserAuthentication(BaseModel):
    """User authentication information."""
    email: Optional[str] = Field(default=None, description="User email address")
    email_verified: bool = Field(default=False, description="Email verification status")
    telegram_id: Optional[int] = Field(default=None, description="Telegram user ID")
    phone_number: Optional[str] = Field(default=None, description="User's phone number")
    auth_method: AuthMethod = Field(default=AuthMethod.EMAIL, description="Primary authentication method")
    
    # Security fields
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")
    failed_login_attempts: int = Field(default=0, ge=0, description="Failed login attempts")
    account_locked_until: Optional[datetime] = Field(default=None, description="Account lockout expiry")

class UserProfile(BaseModel):
    """Complete user profile information."""
    user_id: int = Field(description="Unique user identifier")
    username: Optional[str] = Field(default=None, description="Username (for Telegram)")
    first_name: Optional[str] = Field(default=None, description="User's first name")
    last_name: Optional[str] = Field(default=None, description="User's last name")
    
    # Contact information
    contact_shared: bool = Field(default=False, description="Whether contact is shared")
    is_admin: bool = Field(default=False, description="Admin status")
    
    # Embedded related data
    auth: Optional[UserAuthentication] = Field(default=None, description="Authentication information")
    preferences: Optional[UserPreferences] = Field(default=None, description="User preferences")
    credits: Optional[UserCredits] = Field(default=None, description="Credit information")
    subscription: Optional[UserSubscription] = Field(default=None, description="Subscription details")
    
    # Timestamps
    created_at: Optional[datetime] = Field(default=None, description="Account creation date")
    updated_at: Optional[datetime] = Field(default=None, description="Last profile update")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")
    
    # Personal prompt settings
    personal_prompt_text: Optional[str] = Field(default=None, max_length=4000, description="User's personal prompt")
    personal_prompt_validated: bool = Field(default=False, description="Prompt validation status")
    personal_prompt_validation_error: Optional[str] = Field(default=None, description="Prompt validation error")
    personal_prompt_updated: Optional[datetime] = Field(default=None, description="Prompt last update")
    
    # Blocking information
    is_blocked: bool = Field(default=False, description="User blocked status")
    blocked_reason: Optional[str] = Field(default=None, description="Reason for blocking")
    blocked_at: Optional[datetime] = Field(default=None, description="When user was blocked")
    blocked_until: Optional[datetime] = Field(default=None, description="Block expiry date")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class UserProfileCreate(LanguageValidatorMixin, RoleValidatorMixin):
    """Schema for creating a new user profile."""
    # Required fields
    email: str = Field(description="User email address")
    password: str = Field(description="User password")
    
    # Optional profile information
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    username: Optional[str] = Field(default=None, description="Username (for Telegram)")
    phone_number: Optional[str] = Field(default=None, description="Phone number")
    
    # Optional preferences during creation
    language: Optional[str] = Field(default=DEFAULT_LANGUAGE)
    role: Optional[UserRole] = Field(default=UserRole.USER)
    
    # Telegram linking
    telegram_id: Optional[int] = Field(default=None, description="Telegram user ID for linking")
    auth_method: AuthMethod = Field(default=AuthMethod.EMAIL, description="Authentication method")

class UserProfileUpdate(LanguageValidatorMixin, RoleValidatorMixin):
    """Schema for updating user profile."""
    # Basic profile updates
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    username: Optional[str] = Field(default=None)
    phone_number: Optional[str] = Field(default=None)
    contact_shared: Optional[bool] = Field(default=None)
    
    # Preferences updates
    language: Optional[str] = Field(default=None)
    role: Optional[UserRole] = Field(default=None)
    audio_language: Optional[str] = Field(default=None)
    output_language: Optional[str] = Field(default=None)
    
    # UI preferences
    notifications_enabled: Optional[bool] = Field(default=None)
    dark_mode: Optional[bool] = Field(default=None)
    auto_transcribe: Optional[bool] = Field(default=None)
    
    # Personal prompt updates
    personal_prompt_text: Optional[str] = Field(default=None, max_length=4000)

class UserFlowState(BaseModel):
    """User onboarding flow state."""
    user_id: int
    current_step: str = Field(description="Current step in user flow")
    completed_steps: List[str] = Field(default_factory=list, description="Completed onboarding steps")
    next_required_step: Optional[str] = Field(default=None, description="Next required step")
    is_complete: bool = Field(default=False, description="Whether onboarding is complete")
    
    # Flow metadata
    flow_type: str = Field(default="email_registration", description="Type of onboarding flow")
    started_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class UserStatistics(BaseModel):
    """User usage statistics."""
    user_id: int
    
    # Usage metrics
    total_audio_sessions: int = Field(default=0, ge=0)
    total_tokens_used: int = Field(default=0, ge=0)
    total_cost_usd: float = Field(default=0.0, ge=0.0)
    average_session_duration: Optional[float] = Field(default=None, ge=0.0)
    
    # Time-based metrics
    last_7_days_sessions: int = Field(default=0, ge=0)
    last_30_days_sessions: int = Field(default=0, ge=0)
    current_month_credits: int = Field(default=0, ge=0)
    
    # Quality metrics
    success_rate: float = Field(default=100.0, ge=0.0, le=100.0)
    average_rating: Optional[float] = Field(default=None, ge=1.0, le=5.0)
    
    # Engagement metrics
    login_streak: int = Field(default=0, ge=0, description="Consecutive days logged in")
    total_logins: int = Field(default=0, ge=0)
    features_used: List[str] = Field(default_factory=list, description="Features user has used")

class UserListResponse(BaseModel):
    """Response schema for user list with pagination."""
    users: List[UserProfile]
    pagination: Dict[str, Any] = Field(description="Pagination information")
    total_users: int = Field(ge=0)
    current_page: int = Field(ge=1)
    per_page: int = Field(ge=1)
    total_pages: int = Field(ge=0)
    
    # Additional metadata
    filters_applied: Dict[str, Any] = Field(default_factory=dict)
    sort_by: Optional[str] = Field(default=None)
    sort_order: str = Field(default="desc")

class PublicUserProfile(BaseModel):
    """Public-facing user profile (limited fields for privacy)."""
    user_id: int
    username: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    display_name: str = Field(description="Computed display name")
    is_admin: bool = Field(default=False)
    subscription_tier: SubscriptionType
    member_since: Optional[datetime] = Field(default=None)
    
    # Public stats
    public_stats: Optional[Dict[str, Any]] = Field(default=None, description="Public statistics")

class UserSearchRequest(BaseModel):
    """Schema for searching users."""
    query: Optional[str] = Field(default=None, description="Search query")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    sort_by: Optional[str] = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)

class UserBulkAction(BaseModel):
    """Schema for bulk actions on users."""
    user_ids: List[int] = Field(description="List of user IDs")
    action: str = Field(description="Action to perform")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    reason: Optional[str] = Field(default=None, description="Reason for bulk action")

# Account linking schemas
class TelegramLinkRequest(BaseModel):
    """Schema for linking Telegram account."""
    email: str = Field(description="Email address to link")
    telegram_id: int = Field(description="Telegram user ID")
    verification_code: Optional[str] = Field(default=None, description="Optional verification code")

class AccountUnlinkRequest(BaseModel):
    """Schema for unlinking accounts."""
    auth_method: AuthMethod = Field(description="Authentication method to unlink")
    confirmation_password: str = Field(description="Password confirmation for security") 