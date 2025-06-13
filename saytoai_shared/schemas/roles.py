"""
Advanced Role Management and Prompt Customization schemas for SayToAI ecosystem.
Supports scalable role management and multi-context prompt customization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum
from ..constants import (
    UserRole,
    MAX_CUSTOM_PROMPT_LENGTH,
    SUPPORTED_LANGUAGES
)

class PromptContext(str, Enum):
    """Different contexts where prompts can be applied."""
    DEVELOPER = "developer"          # Software development and programming
    DESIGNER = "designer"            # UI/UX and creative design
    AI_CHAT = "ai_chat"             # General AI conversation

class PromptType(str, Enum):
    """Types of prompts."""
    SYSTEM = "system"               # System-level prompts
    USER_PERSONAL = "user_personal"  # User's personal prompt
    ROLE_DEFAULT = "role_default"   # Default prompt for a role
    CONTEXT_SPECIFIC = "context_specific"  # Context-specific prompt

class RolePermission(str, Enum):
    """Granular permissions for roles."""
    # Basic permissions
    USE_BASIC_FEATURES = "use_basic_features"
    UPLOAD_AUDIO = "upload_audio"
    VIEW_HISTORY = "view_history"
    
    # Advanced permissions
    CUSTOM_PROMPTS = "custom_prompts"
    MULTIPLE_PROMPTS = "multiple_prompts"
    ADVANCED_SETTINGS = "advanced_settings"
    
    # Admin permissions
    VIEW_USERS = "view_users"
    MANAGE_USERS = "manage_users"
    VIEW_ANALYTICS = "view_analytics"
    SYSTEM_SETTINGS = "system_settings"
    
    # Super admin permissions
    MANAGE_ROLES = "manage_roles"
    SYSTEM_ADMINISTRATION = "system_administration"

class UserRoleDefinition(BaseModel):
    """Enhanced role definition with permissions and limits."""
    role: UserRole = Field(description="Role identifier")
    display_name: str = Field(description="Human-readable role name")
    description: str = Field(description="Role description")
    
    # Permissions
    permissions: List[RolePermission] = Field(description="List of role permissions")
    
    # Limits
    max_custom_prompts: int = Field(default=1, ge=0, description="Maximum custom prompts allowed")
    max_prompt_length: int = Field(default=MAX_CUSTOM_PROMPT_LENGTH, description="Maximum prompt length")
    monthly_credit_limit: int = Field(default=50, ge=0, description="Monthly credit limit")
    
    # Features
    can_use_contexts: List[PromptContext] = Field(default_factory=list, description="Available prompt contexts")
    default_context: PromptContext = Field(default=PromptContext.AI_CHAT, description="Default prompt context")
    
    # Metadata
    is_active: bool = Field(default=True, description="Whether role is active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class CustomPrompt(BaseModel):
    """Individual custom prompt schema."""
    id: Optional[int] = Field(default=None, description="Prompt ID")
    user_id: int = Field(description="User who owns this prompt")
    
    # Prompt content
    name: str = Field(max_length=100, description="Prompt name/title")
    content: str = Field(max_length=MAX_CUSTOM_PROMPT_LENGTH, description="Prompt content")
    
    # Context and targeting
    context: PromptContext = Field(default=PromptContext.AI_CHAT, description="Prompt context")
    prompt_type: PromptType = Field(default=PromptType.USER_PERSONAL, description="Prompt type")
    language: str = Field(default="english", description="Prompt language")
    
    # Validation and status
    is_validated: bool = Field(default=False, description="Whether prompt passed validation")
    validation_error: Optional[str] = Field(default=None, description="Validation error message")
    is_active: bool = Field(default=True, description="Whether prompt is active")
    
    # Usage tracking
    usage_count: int = Field(default=0, ge=0, description="How many times used")
    last_used: Optional[datetime] = Field(default=None, description="Last usage timestamp")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('language')
    def validate_language(cls, v):
        if v not in SUPPORTED_LANGUAGES:
            raise ValueError(f'Language must be one of: {SUPPORTED_LANGUAGES}')
        return v

class PromptTemplate(BaseModel):
    """System-provided prompt templates."""
    id: Optional[int] = Field(default=None)
    name: str = Field(description="Template name")
    description: str = Field(description="Template description")
    content: str = Field(description="Template content with placeholders")
    
    # Targeting
    context: PromptContext = Field(description="Template context")
    recommended_roles: List[UserRole] = Field(default_factory=list, description="Recommended for roles")
    
    # Customization
    variables: List[str] = Field(default_factory=list, description="Available variables for customization")
    is_customizable: bool = Field(default=True, description="Whether users can modify")
    
    # Metadata
    created_by: str = Field(description="Creator (system/admin)")
    version: str = Field(default="1.0", description="Template version")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)

class UserRoleAssignment(BaseModel):
    """User role assignment with role-specific settings."""
    user_id: int = Field(description="User identifier")
    role: UserRole = Field(description="Assigned role")
    
    # Role-specific overrides
    custom_permissions: List[RolePermission] = Field(default_factory=list, description="Additional permissions")
    permission_overrides: Dict[str, bool] = Field(default_factory=dict, description="Permission overrides")
    
    # Limits (can override role defaults)
    custom_prompt_limit: Optional[int] = Field(default=None, description="Custom prompt limit override")
    credit_limit_override: Optional[int] = Field(default=None, description="Credit limit override")
    
    # Assignment metadata
    assigned_by: Optional[int] = Field(default=None, description="Admin who assigned role")
    assigned_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = Field(default=None, description="Role expiry (if temporary)")
    
    # Status
    is_active: bool = Field(default=True)
    notes: Optional[str] = Field(default=None, description="Assignment notes")

class PromptUsageLog(BaseModel):
    """Log prompt usage for analytics."""
    id: Optional[int] = Field(default=None)
    user_id: int = Field(description="User who used prompt")
    prompt_id: int = Field(description="Prompt that was used")
    
    # Usage context
    context: PromptContext = Field(description="Context where prompt was used")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    
    # Performance metrics
    input_tokens: int = Field(ge=0, description="Input tokens")
    output_tokens: int = Field(ge=0, description="Output tokens")
    processing_time_ms: float = Field(ge=0.0, description="Processing time")
    
    # Quality metrics
    user_rating: Optional[int] = Field(default=None, ge=1, le=5, description="User rating")
    success: bool = Field(default=True, description="Whether execution was successful")
    error_message: Optional[str] = Field(default=None, description="Error if failed")
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    user_agent: Optional[str] = Field(default=None)
    ip_address: Optional[str] = Field(default=None)

# Request/Response schemas
class CreatePromptRequest(BaseModel):
    """Request to create a new custom prompt."""
    name: str = Field(max_length=100, description="Prompt name")
    content: str = Field(max_length=MAX_CUSTOM_PROMPT_LENGTH, description="Prompt content")
    context: PromptContext = Field(default=PromptContext.AI_CHAT, description="Prompt context")
    language: str = Field(default="english", description="Prompt language")

class UpdatePromptRequest(BaseModel):
    """Request to update an existing prompt."""
    name: Optional[str] = Field(default=None, max_length=100)
    content: Optional[str] = Field(default=None, max_length=MAX_CUSTOM_PROMPT_LENGTH)
    context: Optional[PromptContext] = Field(default=None)
    language: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)

class PromptListResponse(BaseModel):
    """Response for listing user prompts."""
    prompts: List[CustomPrompt] = Field(description="User's prompts")
    total_prompts: int = Field(ge=0, description="Total prompt count")
    active_prompts: int = Field(ge=0, description="Active prompt count")
    contexts_used: List[PromptContext] = Field(description="Contexts user has prompts for")
    
    # Limits
    max_prompts_allowed: int = Field(description="Maximum prompts user can create")
    can_create_more: bool = Field(description="Whether user can create more prompts")

class RoleCapabilities(BaseModel):
    """What a role can do - used for frontend features."""
    role: UserRole
    permissions: List[RolePermission]
    max_custom_prompts: int
    available_contexts: List[PromptContext]
    features: Dict[str, bool] = Field(description="Feature flags for this role")

class PromptValidationResult(BaseModel):
    """Result of prompt validation."""
    is_valid: bool = Field(description="Whether prompt is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    estimated_tokens: Optional[int] = Field(default=None, description="Estimated token count")
    estimated_cost: Optional[float] = Field(default=None, description="Estimated cost per use") 