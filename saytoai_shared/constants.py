"""
SayToAI Shared Constants
========================

Shared constants and enums for all SayToAI applications.
"""

from enum import Enum
from typing import Dict, Any, List

# ============================================================================
# CORE SERVICE CONFIGURATION
# ============================================================================

SERVICE_TIERS = ["free_trial", "free", "basic", "standard", "premium"]
INITIAL_FREE_CREDITS = 50
DEFAULT_LANGUAGE = "uz"
DEFAULT_AUDIO_LANGUAGE = "uz"
DEFAULT_OUTPUT_LANGUAGE = "uz"

# ============================================================================
# ENUMS
# ============================================================================

class SubscriptionType(Enum):
    """Subscription types."""
    FREE_TRIAL = "free_trial"
    FREE = "free"
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"

class SubscriptionStatus(Enum):
    """Subscription status."""
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"

class PaymentStatus(Enum):
    """Payment status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class RequestStatus(Enum):
    """Request status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class LogLevel(Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class Platform(Enum):
    """Platform types."""
    WEB = "web"
    TELEGRAM = "telegram"
    MOBILE = "mobile"
    API = "api"

class UserRole(Enum):
    """User roles."""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class TaskStatus(Enum):
    """Task status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkerStatus(Enum):
    """Worker status."""
    IDLE = "idle"
    BUSY = "busy"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"

# ============================================================================
# ADMIN AND SYSTEM
# ============================================================================

ADMIN_PHONE = "+998901234567"
SUPER_ADMIN_PHONE = "+998901234567"

# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

MAX_CUSTOM_PROMPT_LENGTH = 1000
MAX_CUSTOM_PROMPT_COUNT = 10
MAX_AUDIO_DURATION_SECONDS = 3600
MAX_FILE_SIZE_MB = 25

# ============================================================================
# AUTHENTICATION
# ============================================================================

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
EMAIL_CODE_LENGTH = 6
EMAIL_CODE_EXPIRATION_MINUTES = 15
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

# ============================================================================
# UTILITY MAPPINGS
# ============================================================================

SUBSCRIPTION_TYPES = {
    SubscriptionType.FREE_TRIAL: "free_trial",
    SubscriptionType.FREE: "free",
    SubscriptionType.BASIC: "basic",
    SubscriptionType.STANDARD: "standard",
    SubscriptionType.PREMIUM: "premium"
}

PAYMENT_STATUSES = {
    PaymentStatus.PENDING: "pending",
    PaymentStatus.PROCESSING: "processing",
    PaymentStatus.COMPLETED: "completed",
    PaymentStatus.FAILED: "failed",
    PaymentStatus.CANCELLED: "cancelled",
    PaymentStatus.REFUNDED: "refunded"
}

LOG_LEVELS = {
    LogLevel.DEBUG: "debug",
    LogLevel.INFO: "info",
    LogLevel.WARNING: "warning",
    LogLevel.ERROR: "error",
    LogLevel.CRITICAL: "critical"
}

PLATFORMS = {
    Platform.WEB: "web",
    Platform.TELEGRAM: "telegram",
    Platform.MOBILE: "mobile",
    Platform.API: "api"
}

USER_ROLES = {
    UserRole.USER: "user",
    UserRole.ADMIN: "admin",
    UserRole.SUPER_ADMIN: "super_admin"
} 