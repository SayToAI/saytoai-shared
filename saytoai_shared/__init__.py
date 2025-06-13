"""
SayToAI Shared Package
=====================

Production-ready shared library for the SayToAI ecosystem.

This package provides:
- 📊 Centralized constants and enums
- 🏗️ Pydantic data models for all services
- 🛠️ Utility functions for validation, formatting, and processing
- 🔧 Service implementations for SMS, payments, and authentication
- 🧪 Comprehensive test suite (45 tests, 100% passing)

Architecture:
- saytoai-frontend (React + TypeScript) → api.saytoai.org
- saytoai-backend (FastAPI + Python) → Uses this package
- saytoai-bot (aiogram + Python) → Uses this package  
- saytoai-admin-frontend (React + TypeScript) → admin.saytoai.org
- saytoai-admin-backend (FastAPI + Python) → Uses this package
- saytoai-shared (This package) → Shared across all services

Version: 0.0.1 (Released: 2025-06-14)
Python: 3.12+
License: MIT
"""

# Package metadata
__version__ = "0.0.1"
__author__ = "SayToAI Team"
__email__ = "saytoaiapp@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 SayToAI Team"

# ============================================================================
# IMPORTS - Core Components Available at Package Level
# ============================================================================

# Import commonly used constants and enums for easy access
from .constants import (
    SERVICE_TIERS,
    SUBSCRIPTION_TYPES,
    PAYMENT_STATUSES,
    LOG_LEVELS,
    PLATFORMS,
    INITIAL_FREE_CREDITS,
    ADMIN_PHONE,
    SUPER_ADMIN_PHONE,
    UserRole,
    SubscriptionType,
    PaymentStatus,
    AuthMethod,
    EmailCodePurpose
)

# Import user-related schemas and models
from .schemas.user import (
    UserProfile,
    UserPreferences,
    UserCredits,
    UserSubscription,
    UserAuthentication,
    UserProfileCreate,
    UserProfileUpdate,
    TelegramLinkRequest
)

# Import service-related schemas and configurations
from .schemas.service import (
    ServiceAccess,
    PaymentInfo,
    AudioSession,
    ServiceStatus,
    SystemMetrics
)

# Import authentication and registration schemas
from .schemas.auth import (
    RegistrationRequest,
    LoginRequest,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    ForgotPasswordRequest,
    ResetPasswordConfirm,
    AuthToken,
    UserSession,
    RegistrationResponse,
    LoginResponse
)

# Import commonly used utility functions
from .utils import (
    sanitize_username,
    validate_phone_number,
    format_datetime,
    get_user_flow_state,
    split_long_message,
    calculate_credits_needed,
    generate_order_id,
    generate_payment_order_id,
    parse_error_message,
    get_display_name
)

# ============================================================================
# PUBLIC API - Exported Components
# ============================================================================

__all__ = [
    # Constants and Enums
    "SERVICE_TIERS",
    "SUBSCRIPTION_TYPES", 
    "PAYMENT_STATUSES",
    "LOG_LEVELS",
    "PLATFORMS",
    "INITIAL_FREE_CREDITS",
    "ADMIN_PHONE",
    "SUPER_ADMIN_PHONE",
    "UserRole",
    "SubscriptionType",
    "PaymentStatus",
    "AuthMethod",
    "EmailCodePurpose",
    
    # User schemas
    "UserProfile",
    "UserPreferences", 
    "UserCredits",
    "UserSubscription",
    "UserAuthentication",
    "UserProfileCreate",
    "UserProfileUpdate",
    "TelegramLinkRequest",
    
    # Service schemas
    "ServiceAccess",
    "PaymentInfo",
    "AudioSession",
    "ServiceStatus",
    "SystemMetrics",
    
    # Auth schemas
    "RegistrationRequest",
    "LoginRequest",
    "EmailVerificationRequest",
    "EmailVerificationConfirm",
    "ForgotPasswordRequest",
    "ResetPasswordConfirm",
    "AuthToken",
    "UserSession",
    "RegistrationResponse",
    "LoginResponse",
    
    # Utilities
    "sanitize_username",
    "validate_phone_number",
    "format_datetime",
    "get_user_flow_state",
    "split_long_message",
    "calculate_credits_needed",
    "generate_order_id",
    "generate_payment_order_id",
    "parse_error_message",
    "get_display_name"
] 