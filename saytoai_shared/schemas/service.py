"""
Service-related Pydantic schemas for SayToAI ecosystem.
Extracted and adapted from voiceBot database models and API structures.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..constants import (
    PaymentStatus,
    Platform,
    TaskStatus,
    WorkerStatus,
    LogLevel,
    SUPPORTED_PAYMENT_METHODS,
    SUPPORTED_CURRENCIES,
    DEFAULT_CURRENCY
)

class ServiceAccess(BaseModel):
    """Service access and tier information."""
    service_name: str = Field(description="Name of the service")
    tier: str = Field(description="Service tier (free, pro, enterprise)")
    status: str = Field(description="Access status (active, expired, suspended)")
    features: List[str] = Field(default_factory=list, description="Available features")
    limits: Dict[str, Any] = Field(default_factory=dict, description="Service limits")
    expires_at: Optional[datetime] = Field(default=None, description="Service expiry date")

class PaymentInfo(BaseModel):
    """Payment transaction information."""
    id: Optional[int] = Field(default=None, description="Payment ID")
    user_id: int = Field(description="User identifier")
    credits_purchased: int = Field(ge=1, description="Number of credits purchased")
    amount_paid: int = Field(ge=0, description="Amount paid in smallest currency unit")
    payment_method: str = Field(description="Payment method used")
    payment_system: Optional[str] = Field(default=None, description="Detailed payment system")
    order_id: Optional[str] = Field(default=None, description="External order ID")
    transaction_id: Optional[str] = Field(default=None, description="Transaction ID")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Payment status")
    
    # Payment URL and tracking
    payment_url: Optional[str] = Field(default=None, description="Payment URL")
    expires_at: Optional[datetime] = Field(default=None, description="Payment URL expiry")
    
    # Detailed information
    tariff_name: Optional[str] = Field(default=None, description="Tariff name")
    currency: str = Field(default=DEFAULT_CURRENCY, description="Payment currency")
    exchange_rate: Optional[float] = Field(default=None, description="Exchange rate if applicable")
    
    # Credit balance tracking
    previous_credits: int = Field(default=0, ge=0, description="Previous credit balance")
    new_credits: int = Field(default=0, ge=0, description="New credit balance")
    
    # Timestamps
    created_at: Optional[datetime] = Field(default=None, description="Payment creation date")
    processed_at: Optional[datetime] = Field(default=None, description="Payment processing date")
    expired_at: Optional[datetime] = Field(default=None, description="Payment expiry date")
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in SUPPORTED_PAYMENT_METHODS:
            raise ValueError(f'Payment method must be one of: {SUPPORTED_PAYMENT_METHODS}')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        if v not in SUPPORTED_CURRENCIES:
            raise ValueError(f'Currency must be one of: {SUPPORTED_CURRENCIES}')
        return v

class PaymentCreate(BaseModel):
    """Schema for creating a payment."""
    user_id: int = Field(description="User identifier")
    credits_purchased: int = Field(ge=1, description="Number of credits to purchase")
    payment_method: str = Field(description="Payment method")
    tariff_name: Optional[str] = Field(default=None, description="Tariff name")
    currency: str = Field(default=DEFAULT_CURRENCY, description="Payment currency")
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in SUPPORTED_PAYMENT_METHODS:
            raise ValueError(f'Payment method must be one of: {SUPPORTED_PAYMENT_METHODS}')
        return v


class AudioSession(BaseModel):
    """Audio processing session information."""
    id: Optional[int] = Field(default=None, description="Session ID")
    user_id: int = Field(description="User identifier")
    
    # Processing metrics
    duration_seconds: Optional[int] = Field(default=None, ge=0, description="Audio duration in seconds")
    input_tokens: int = Field(ge=0, description="Input tokens used")
    output_tokens: int = Field(ge=0, description="Output tokens generated")
    cost_usd: float = Field(ge=0.0, description="Processing cost in USD")
    
    # Processing status
    processing_result: Optional[str] = Field(default=None, description="Processing result")
    
    # Timestamps  
    submitted_at: Optional[datetime] = Field(default=None, description="Session submission time")
    completed_at: Optional[datetime] = Field(default=None, description="Session completion time")

class ServiceStatus(BaseModel):
    """Service health and status information."""
    service_name: str = Field(description="Service name")
    status: str = Field(description="Service status (up, down, degraded)")
    health_score: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Health score percentage")
    uptime_seconds: Optional[int] = Field(default=None, ge=0, description="Uptime in seconds")
    last_check: Optional[datetime] = Field(default=None, description="Last health check time")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional status details")

class SystemMetrics(BaseModel):
    """System performance metrics."""
    timestamp: datetime = Field(description="Metrics timestamp")
    
    # System resources
    cpu_usage_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    memory_usage_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    disk_usage_percent: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    
    # Application metrics
    active_users: Optional[int] = Field(default=None, ge=0)
    total_requests: Optional[int] = Field(default=None, ge=0)
    successful_requests: Optional[int] = Field(default=None, ge=0)
    failed_requests: Optional[int] = Field(default=None, ge=0)
    average_response_time_ms: Optional[float] = Field(default=None, ge=0.0)
    
    # Worker metrics
    active_workers: Optional[int] = Field(default=None, ge=0)
    idle_workers: Optional[int] = Field(default=None, ge=0)
    error_workers: Optional[int] = Field(default=None, ge=0)
    queue_size: Optional[int] = Field(default=None, ge=0)
    
    # Business metrics
    credits_consumed_last_hour: Optional[int] = Field(default=None, ge=0)
    new_users_last_hour: Optional[int] = Field(default=None, ge=0)
    payments_completed_last_hour: Optional[int] = Field(default=None, ge=0)

class WorkerInfo(BaseModel):
    """Worker system information."""
    worker_id: str = Field(description="Worker identifier")
    status: WorkerStatus = Field(description="Worker status")
    current_task: Optional[str] = Field(default=None, description="Current task identifier")
    tasks_completed: int = Field(default=0, ge=0, description="Total completed tasks")
    tasks_failed: int = Field(default=0, ge=0, description="Total failed tasks")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")
    api_key_name: Optional[str] = Field(default=None, description="Associated API key")

class TaskInfo(BaseModel):
    """Task processing information."""
    task_id: str = Field(description="Task identifier")
    user_id: int = Field(description="User who submitted task")
    task_type: str = Field(description="Type of task")
    status: TaskStatus = Field(description="Task status")
    priority: int = Field(default=0, description="Task priority")
    
    # Processing details
    worker_id: Optional[str] = Field(default=None, description="Assigned worker")
    processing_time_seconds: Optional[float] = Field(default=None, ge=0.0)
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    
    # Timestamps
    created_at: datetime = Field(description="Task creation time")
    started_at: Optional[datetime] = Field(default=None, description="Processing start time")
    completed_at: Optional[datetime] = Field(default=None, description="Processing completion time")

class ActivityLog(BaseModel):
    """System activity log entry."""
    id: Optional[int] = Field(default=None, description="Log entry ID")
    user_id: Optional[int] = Field(default=None, description="User identifier (if applicable)")
    action_type: str = Field(description="Type of action performed")
    platform: Platform = Field(description="Platform where action occurred")
    
    # Context and details
    context_data: Optional[Dict[str, Any]] = Field(default=None, description="Additional context data")
    anonymous_user_id: Optional[str] = Field(default=None, description="Anonymous user identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    
    # Timestamps
    timestamp: datetime = Field(description="Action timestamp")

class ApiKeyStatus(BaseModel):
    """API key status information."""
    key_name: str = Field(description="API key identifier")
    is_active: bool = Field(description="Whether key is active")
    daily_usage: int = Field(default=0, ge=0, description="Usage count today")
    total_usage: int = Field(default=0, ge=0, description="Total usage count")
    rate_limited_until: Optional[datetime] = Field(default=None, description="Rate limit reset time")
    consecutive_failures: int = Field(default=0, ge=0, description="Consecutive failure count")
    last_used: Optional[datetime] = Field(default=None, description="Last usage timestamp")

class SystemHealth(BaseModel):
    """Overall system health status."""
    overall_status: str = Field(description="Overall system status")
    health_score: float = Field(ge=0.0, le=100.0, description="Overall health score")
    services: List[ServiceStatus] = Field(description="Individual service statuses")
    metrics: SystemMetrics = Field(description="Current system metrics")
    issues: List[str] = Field(default_factory=list, description="Current system issues")
    last_updated: datetime = Field(description="Last health check time")

class LogEntry(BaseModel):
    """System log entry."""
    level: LogLevel = Field(description="Log level")
    service: str = Field(description="Service name")
    message: str = Field(description="Log message")
    timestamp: str = Field(description="Formatted timestamp") 
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")

class PaginationInfo(BaseModel):
    """Pagination information for list responses."""
    current_page: int = Field(ge=1, description="Current page number")
    per_page: int = Field(ge=1, description="Items per page")
    total_items: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")
    has_prev: bool = Field(description="Whether previous page exists")
    has_next: bool = Field(description="Whether next page exists") 