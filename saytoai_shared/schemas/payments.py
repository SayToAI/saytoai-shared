"""
Shared payment schemas and models for SayToAI ecosystem.
Contains reusable payment data structures - NOT business logic.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from ..constants import PaymentStatus

# ===== PAYMENT PROVIDER ENUMS =====

class PaymentProvider(str, Enum):
    """Supported payment providers."""
    PAYME = "payme"
    CLICK = "click"

class PaymentMethod(str, Enum):
    """Payment method types."""
    CARD = "card"
    WALLET = "wallet"
    BANK_TRANSFER = "bank_transfer"

class TransactionType(str, Enum):
    """Transaction types."""
    PAYMENT = "payment"
    REFUND = "refund"

# ===== SHARED PAYMENT REQUEST/RESPONSE MODELS =====

class PaymentRequest(BaseModel):
    """Base payment request model - updated to match voiceBot structure."""
    amount: Decimal = Field(..., description="Payment amount in smallest currency unit (tiyin)")
    currency: str = Field("UZS", description="Payment currency")
    order_id: str = Field(..., description="Unique order identifier")
    description: str = Field(..., description="Payment description")
    user_id: str = Field(..., description="User making the payment")
    tariff_name: Optional[str] = Field(None, description="Tariff name (basic, standard, premium)")
    credits_purchased: int = Field(..., description="Number of credits being purchased")
    payment_method: str = Field(..., description="Payment method (payme, click)")
    payment_system: Optional[str] = Field(None, description="Detailed payment system info")
    return_url: Optional[str] = Field(None, description="Return URL after payment")
    callback_url: Optional[str] = Field(None, description="Webhook callback URL")
    expires_at: Optional[datetime] = Field(None, description="Payment URL expiry time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": "2500000",  # 2,500,000 UZS in tiyin
                "currency": "UZS",
                "order_id": "order_123456",
                "description": "SayToAI Premium Subscription",
                "user_id": "user_789",
                "tariff_name": "basic",
                "credits_purchased": 60,
                "payment_method": "payme",
                "payment_system": "payme_checkout",
                "return_url": "https://t.me/saytoai_bot?start=payment_success",
                "callback_url": "https://api.saytoai.org/webhooks/payment",
                "expires_at": "2024-01-01T13:00:00Z"
            }
        }

class PaymentResponse(BaseModel):
    """Base payment response model - updated to match voiceBot structure."""
    payment_id: str = Field(..., description="Internal payment identifier")
    order_id: str = Field(..., description="Order identifier")
    status: PaymentStatus = Field(..., description="Payment status")
    amount: Decimal = Field(..., description="Payment amount in smallest currency unit")
    currency: str = Field(..., description="Payment currency")
    provider: PaymentProvider = Field(..., description="Payment provider")
    payment_url: Optional[str] = Field(None, description="Payment URL for user")
    credits_purchased: int = Field(..., description="Number of credits purchased")
    tariff_name: Optional[str] = Field(None, description="Tariff name")
    payment_method: str = Field(..., description="Payment method")
    payment_system: Optional[str] = Field(None, description="Payment system details")
    previous_credits: int = Field(0, description="User's previous credit balance")
    new_credits: int = Field(..., description="User's new credit balance after payment")
    expires_at: Optional[datetime] = Field(None, description="Payment URL expiry time")
    created_at: datetime = Field(..., description="Payment creation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "payment_id": "pay_12345",
                "order_id": "order_123456",
                "status": "pending",
                "amount": "100000",
                "currency": "UZS",
                "provider": "payme",
                "payment_url": "https://checkout.paycom.uz/...",
                "credits_purchased": 60,
                "tariff_name": "basic",
                "payment_method": "payme",
                "payment_system": "payme_checkout",
                "previous_credits": 10,
                "new_credits": 70,
                "expires_at": "2024-01-01T13:00:00Z",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }

# ===== WEBHOOK DATA MODELS =====

class PaymeWebhookData(BaseModel):
    """Payme webhook data structure."""
    id: str = Field(..., description="Transaction ID")
    time: int = Field(..., description="Transaction timestamp")
    amount: int = Field(..., description="Amount in tiyin (1/100 UZS)")
    account: Dict[str, Any] = Field(..., description="Account information")
    create_time: int = Field(..., description="Creation timestamp")
    perform_time: Optional[int] = Field(None, description="Perform timestamp")
    cancel_time: Optional[int] = Field(None, description="Cancel timestamp")
    transaction: str = Field(..., description="Transaction ID")
    state: int = Field(..., description="Transaction state")
    reason: Optional[int] = Field(None, description="Cancel reason")

class ClickWebhookData(BaseModel):
    """Click webhook data structure."""
    click_trans_id: str = Field(..., description="Click transaction ID")
    service_id: str = Field(..., description="Service ID")
    click_paydoc_id: str = Field(..., description="Click payment document ID")
    merchant_trans_id: str = Field(..., description="Merchant transaction ID")
    amount: Decimal = Field(..., description="Payment amount")
    action: int = Field(..., description="Action type (0=prepare, 1=complete)")
    error: int = Field(..., description="Error code")
    error_note: str = Field(..., description="Error description")
    sign_time: str = Field(..., description="Signature timestamp")
    sign_string: str = Field(..., description="Signature string")

# ===== PAYMENT HISTORY AND TRACKING =====

class PaymentTransaction(BaseModel):
    """Payment transaction record - matching voiceBot database structure."""
    id: Optional[int] = Field(None, description="Internal transaction ID")
    user_id: int = Field(..., description="User ID")
    
    # Core payment data
    credits_purchased: int = Field(..., description="Number of credits purchased")
    amount_paid: int = Field(..., description="Amount paid in smallest currency unit (tiyin)")
    payment_method: str = Field(..., description="Payment method (payme, click)")
    payment_system: Optional[str] = Field(None, description="Detailed payment system info")
    order_id: Optional[str] = Field(None, description="Unique order identifier")
    transaction_id: Optional[str] = Field(None, description="Transaction ID from provider")
    status: PaymentStatus = Field(PaymentStatus.PENDING, description="Payment status")
    
    # Payment URL and expiry tracking
    payment_url: Optional[str] = Field(None, description="Payment URL for user")
    expires_at: Optional[datetime] = Field(None, description="Payment URL expiry time")
    
    # Enhanced tracking
    tariff_name: Optional[str] = Field(None, description="Tariff name (basic, standard, premium)")
    currency: str = Field("UZS", description="Payment currency")
    exchange_rate: Optional[float] = Field(None, description="Exchange rate if applicable")
    
    # Credit balance tracking for receipts
    previous_credits: int = Field(0, description="User's previous credit balance")
    new_credits: int = Field(0, description="User's new credit balance after payment")
    
    # Timestamps
    created_at: datetime = Field(..., description="Payment creation timestamp")
    processed_at: Optional[datetime] = Field(None, description="Payment processing timestamp")
    expired_at: Optional[datetime] = Field(None, description="Payment expiry timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "user_id": 789456123,
                "credits_purchased": 60,
                "amount_paid": 100000,  # 1000 UZS in tiyin
                "payment_method": "payme",
                "payment_system": "payme_checkout",
                "order_id": "order_789456123_basic_20240101120000_abc12345",
                "transaction_id": "payme_trans_xyz789",
                "status": "pending",
                "payment_url": "https://checkout.paycom.uz/...",
                "expires_at": "2024-01-01T13:00:00Z",
                "tariff_name": "basic",
                "currency": "UZS",
                "exchange_rate": None,
                "previous_credits": 10,
                "new_credits": 70,
                "created_at": "2024-01-01T12:00:00Z",
                "processed_at": None,
                "expired_at": None
            }
        }

class PaymentSummary(BaseModel):
    """Payment summary for user/admin dashboards."""
    total_payments: int = Field(..., description="Total number of payments")
    successful_payments: int = Field(..., description="Number of successful payments")
    failed_payments: int = Field(..., description="Number of failed payments")
    total_amount: Decimal = Field(..., description="Total amount paid")
    currency: str = Field(..., description="Currency")
    last_payment_date: Optional[datetime] = Field(None, description="Last payment date")
    providers_used: List[PaymentProvider] = Field(default_factory=list, description="Providers used")

# ===== ERROR HANDLING =====

class PaymentError(BaseModel):
    """Payment error information."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    provider: PaymentProvider = Field(..., description="Payment provider")
    provider_error: Optional[str] = Field(None, description="Provider-specific error")
    timestamp: datetime = Field(..., description="Error timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "INSUFFICIENT_FUNDS",
                "message": "Insufficient funds on card",
                "provider": "payme",
                "provider_error": "Kartada mablag' yetarli emas",
                "timestamp": "2024-01-01T12:00:00Z"
            }
        }

# ===== VALIDATION HELPERS =====

class PaymentValidationResult(BaseModel):
    """Payment validation result."""
    is_valid: bool = Field(..., description="Whether payment data is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    
class PaymentLimits(BaseModel):
    """Payment limits configuration."""
    min_amount: Decimal = Field(..., description="Minimum payment amount")
    max_amount: Decimal = Field(..., description="Maximum payment amount")
    daily_limit: Optional[Decimal] = Field(None, description="Daily payment limit")
    monthly_limit: Optional[Decimal] = Field(None, description="Monthly payment limit")
    currency: str = Field(..., description="Currency for limits") 