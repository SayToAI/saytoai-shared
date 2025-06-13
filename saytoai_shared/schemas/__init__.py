"""
Shared Pydantic schemas for SayToAI ecosystem.
"""

from .user import (
    UserProfile,
    UserPreferences,
    UserCredits,
    UserSubscription,
    UserAuthentication,
    UserProfileCreate,
    UserProfileUpdate,
    UserFlowState,
    UserStatistics,
    UserListResponse,
    PublicUserProfile,
    TelegramLinkRequest,
    AccountUnlinkRequest
)

from .service import (
    ServiceAccess,
    PaymentInfo,
    AudioSession,
    PaymentCreate,
    ServiceStatus,
    SystemMetrics,
    WorkerInfo,
    TaskInfo,
    ActivityLog,
    ApiKeyStatus,
    SystemHealth,
    LogEntry,
    PaginationInfo
)

from .auth import (
    RegistrationRequest,
    LoginRequest,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    ForgotPasswordRequest,
    ResetPasswordConfirm,
    ChangePasswordRequest,
    AuthToken,
    UserSession,
    EmailCode,
    LoginAttempt,
    AccountLockout,
    SecurityEvent,
    RegistrationResponse,
    LoginResponse,
    VerificationResponse,
    PasswordResetResponse,
    PasswordValidatorMixin,
    EmailValidatorMixin,
    UserRegistrationRequest,
    EmailValidationRequest,
    EmailValidationResponse,
    RegistrationAttemptLog,
    EmailProviderStats,
    AbusePreventionSettings,
    UserRegistrationResponse
)

# Role and prompt management schemas
from .roles import (
    # Enums
    PromptContext,
    PromptType,
    RolePermission,
    
    # Core models
    UserRoleDefinition,
    CustomPrompt,
    PromptTemplate,
    UserRoleAssignment,
    PromptUsageLog,
    
    # Request/Response schemas
    CreatePromptRequest,
    UpdatePromptRequest,
    PromptListResponse,
    RoleCapabilities,
    PromptValidationResult
)

__all__ = [
    # User schemas
    "UserProfile",
    "UserPreferences", 
    "UserCredits",
    "UserSubscription",
    "UserAuthentication",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserFlowState",
    "UserStatistics",
    "UserListResponse",
    "PublicUserProfile",
    "TelegramLinkRequest",
    "AccountUnlinkRequest",
    
    # Service schemas
    "ServiceAccess",
    "PaymentInfo",
    "AudioSession",
    "PaymentCreate",
    "ServiceStatus",
    "SystemMetrics",
    "WorkerInfo",
    "TaskInfo",
    "ActivityLog",
    "ApiKeyStatus",
    "SystemHealth",
    "LogEntry",
    "PaginationInfo",
    
    # Auth schemas
    "RegistrationRequest",
    "LoginRequest",
    "EmailVerificationRequest",
    "EmailVerificationConfirm",
    "ForgotPasswordRequest",
    "ResetPasswordConfirm",
    "ChangePasswordRequest",
    "AuthToken",
    "UserSession",
    "EmailCode",
    "LoginAttempt",
    "AccountLockout",
    "SecurityEvent",
    "RegistrationResponse",
    "LoginResponse",
    "VerificationResponse",
    "PasswordResetResponse",
    "PasswordValidatorMixin",
    "EmailValidatorMixin",
    
    # Role and prompt management
    "PromptContext",
    "PromptType", 
    "RolePermission",
    "UserRoleDefinition",
    "CustomPrompt",
    "PromptTemplate",
    "UserRoleAssignment",
    "PromptUsageLog",
    "CreatePromptRequest",
    "UpdatePromptRequest",
    "PromptListResponse",
    "RoleCapabilities",
    "PromptValidationResult",
    
    # Enhanced authentication
    "UserRegistrationRequest",
    "EmailValidationRequest", 
    "EmailValidationResponse",
    "RegistrationAttemptLog",
    "EmailProviderStats",
    "AbusePreventionSettings",
    "UserRegistrationResponse"
] 