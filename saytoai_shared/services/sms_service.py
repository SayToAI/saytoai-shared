"""
Enhanced SMS Service with workflow management, retry logic, and admin override.
Handles SMS verification with dual delivery methods and comprehensive error handling.
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import httpx

from ..constants import (
    SMSDeliveryMethod,
    SMS_SERVICE_CONFIG,
    SMS_CODE_EXPIRATION_MINUTES,
    SMS_CODE_LENGTH,
    SMS_VERIFICATION_WORKFLOW,
    SMSDeliveryStatus,
    SMSCodePurpose,
    SMSVerificationWorkflowStatus,
    AdminVerificationAction
)
from ..utils import (
    generate_sms_code,
    determine_sms_delivery_method,
    format_sms_message,
    validate_phone_number
)
from ..schemas.sms import (
    SMSVerificationRequest,
    SMSVerificationResponse,
    SMSDeliveryInfo,
    BulkSMSRequest,
    BulkSMSResponse,
    SMSVerificationWorkflowRequest,
    SMSVerificationWorkflowResponse,
    SMSVerificationConfirmationRequest,
    AdminVerificationRequest,
    AdminVerificationResponse,
    SMSWorkflowStatusResponse
)

logger = logging.getLogger(__name__)

class SMSServiceError(Exception):
    """Base exception for SMS service errors."""
    pass

class SMSRateLimitError(SMSServiceError):
    """Raised when SMS rate limit is exceeded."""
    pass

class SMSDeliveryError(SMSServiceError):
    """Raised when SMS delivery fails."""
    pass

class SMSProviderError(SMSServiceError):
    """Raised when SMS provider returns an error."""
    pass

class BaseSMSProvider(ABC):
    """Abstract base class for SMS providers."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = config.get("provider_name", "Unknown")
        self.is_active = config.get("is_active", True)
    
    @abstractmethod
    async def send_sms(self, phone: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send SMS message to phone number."""
        pass
    
    @abstractmethod
    async def check_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """Check delivery status of sent SMS."""
        pass
    
    @abstractmethod
    def get_cost_info(self) -> Dict[str, Any]:
        """Get cost information for this provider."""
        pass

class TelegramSMSService(BaseSMSProvider):
    """SMS service using Telegram bot for delivery."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bot_token = config.get("bot_token")
        self.bot_api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def send_sms(self, phone: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send SMS via Telegram bot."""
        try:
            # Get Telegram user ID from phone number
            telegram_user_id = await self._get_telegram_user_id(phone)
            
            if not telegram_user_id:
                raise SMSDeliveryError(f"No Telegram user found for phone {phone}")
            
            # Send message via Telegram
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.bot_api_url}/sendMessage",
                    json={
                        "chat_id": telegram_user_id,
                        "text": message,
                        "parse_mode": "HTML"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("ok"):
                        return {
                            "success": True,
                            "message_id": str(result["result"]["message_id"]),
                            "delivery_method": SMSDeliveryMethod.TELEGRAM_BOT,
                            "cost": 0.0,
                            "currency": "FREE",
                            "provider": "Telegram Bot",
                            "delivered_at": datetime.now(),
                            "telegram_user_id": telegram_user_id
                        }
                    else:
                        raise SMSProviderError(f"Telegram API error: {result.get('description', 'Unknown error')}")
                else:
                    raise SMSProviderError(f"Telegram API HTTP error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Telegram SMS delivery failed for {phone}: {str(e)}")
            raise SMSDeliveryError(f"Failed to send SMS via Telegram: {str(e)}")
    
    async def check_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """Check delivery status (always successful for Telegram)."""
        return {
            "status": "delivered",
            "delivered_at": datetime.now(),
            "provider": "Telegram Bot"
        }
    
    def get_cost_info(self) -> Dict[str, Any]:
        """Get cost information for Telegram delivery."""
        return {
            "cost_per_sms": 0.0,
            "currency": "FREE",
            "provider": "Telegram Bot",
            "reliability": "very_high"
        }
    
    async def _get_telegram_user_id(self, phone: str) -> Optional[int]:
        """Get Telegram user ID from phone number."""
        # This would typically query your database to find the Telegram user ID
        # associated with the phone number
        # For now, return None to indicate user not found in Telegram
        # Implementation depends on your database structure
        
        # Example implementation:
        # normalized_phone = normalize_phone_for_comparison(phone)
        # user = await db.query("SELECT telegram_user_id FROM users WHERE phone = ?", normalized_phone)
        # return user.telegram_user_id if user else None
        
        return None  # Placeholder - implement based on your database

class ExternalSMSService(BaseSMSProvider):
    """SMS service using external SMS provider (eskiz.uz)."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_url = config.get("api_url", "https://notify.eskiz.uz/api")
        self.email = config.get("email")
        self.password = config.get("password")
        self.access_token = None
        self.token_expires_at = None
    
    async def send_sms(self, phone: str, message: str, **kwargs) -> Dict[str, Any]:
        """Send SMS via external SMS provider."""
        try:
            # Ensure we have a valid access token
            await self._ensure_authenticated()
            
            # Send SMS
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/message/sms/send",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "mobile_phone": phone,
                        "message": message,
                        "from": "4546",  # Default sender ID for eskiz.uz
                        "callback_url": kwargs.get("callback_url")
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        return {
                            "success": True,
                            "message_id": result["data"]["id"],
                            "delivery_method": SMSDeliveryMethod.EXTERNAL_SMS,
                            "cost": SMS_SERVICE_CONFIG["cost_per_sms"],
                            "currency": SMS_SERVICE_CONFIG["currency"],
                            "provider": SMS_SERVICE_CONFIG["provider"],
                            "delivered_at": datetime.now(),
                            "external_id": result["data"]["id"]
                        }
                    else:
                        raise SMSProviderError(f"SMS provider error: {result.get('message', 'Unknown error')}")
                else:
                    raise SMSProviderError(f"SMS provider HTTP error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"External SMS delivery failed for {phone}: {str(e)}")
            raise SMSDeliveryError(f"Failed to send SMS via external provider: {str(e)}")
    
    async def check_delivery_status(self, message_id: str) -> Dict[str, Any]:
        """Check delivery status of sent SMS."""
        try:
            await self._ensure_authenticated()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/message/sms/status/{message_id}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "status": result.get("status", "unknown"),
                        "delivered_at": result.get("delivered_at"),
                        "provider": SMS_SERVICE_CONFIG["provider"]
                    }
                else:
                    return {"status": "unknown", "provider": SMS_SERVICE_CONFIG["provider"]}
        
        except Exception as e:
            logger.error(f"Failed to check SMS delivery status for {message_id}: {str(e)}")
            return {"status": "unknown", "provider": SMS_SERVICE_CONFIG["provider"]}
    
    def get_cost_info(self) -> Dict[str, Any]:
        """Get cost information for external SMS delivery."""
        return {
            "cost_per_sms": SMS_SERVICE_CONFIG["cost_per_sms"],
            "currency": SMS_SERVICE_CONFIG["currency"],
            "provider": SMS_SERVICE_CONFIG["provider"],
            "reliability": "high"
        }
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid access token."""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return
        
        await self._authenticate()
    
    async def _authenticate(self):
        """Authenticate with SMS provider and get access token."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/auth/login",
                    json={
                        "email": self.email,
                        "password": self.password
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") == "success":
                        self.access_token = result["data"]["token"]
                        # Token typically expires in 24 hours
                        self.token_expires_at = datetime.now() + timedelta(hours=23)
                    else:
                        raise SMSProviderError(f"Authentication failed: {result.get('message', 'Unknown error')}")
                else:
                    raise SMSProviderError(f"Authentication HTTP error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"SMS provider authentication failed: {str(e)}")
            raise SMSProviderError(f"Failed to authenticate with SMS provider: {str(e)}")

class SMSService:
    """Main SMS service that orchestrates dual delivery logic."""
    
    def __init__(self, telegram_config: Dict[str, Any] = None, external_config: Dict[str, Any] = None):
        self.telegram_service = TelegramSMSService(telegram_config or {}) if telegram_config else None
        self.external_service = ExternalSMSService(external_config or {}) if external_config else None
        
        # Statistics tracking
        self.stats = {
            "total_sms_sent": 0,
            "telegram_deliveries": 0,
            "external_deliveries": 0,
            "failed_deliveries": 0,
            "total_cost": 0.0
        }
    
    async def send_verification_sms(self, request: SMSVerificationRequest, user_exists_in_telegram: bool = False) -> SMSVerificationResponse:
        """Send SMS verification code with dual delivery logic."""
        try:
            # Validate phone number
            phone_validation = validate_phone_number(request.phone)
            if not phone_validation["is_valid"]:
                raise SMSServiceError(phone_validation["message"])
            
            # Generate verification code
            verification_code = generate_sms_code()
            
            # Format SMS message
            sms_message = format_sms_message(
                "verification_code",
                code=verification_code,
                minutes=SMS_CODE_EXPIRATION_MINUTES
            )
            
            # Determine delivery method
            delivery_info = determine_sms_delivery_method(request.phone, user_exists_in_telegram)
            
            # Send SMS using appropriate method
            delivery_result = await self._send_sms_with_fallback(
                request.phone,
                sms_message,
                delivery_info["method"],
                request.purpose
            )
            
            # Update statistics
            self._update_stats(delivery_result)
            
            # Create response
            return SMSVerificationResponse(
                success=True,
                message="SMS verification code sent successfully",
                phone=request.phone,
                delivery_info=SMSDeliveryInfo(
                    method=delivery_result["delivery_method"],
                    provider=delivery_result["provider"],
                    cost=delivery_result["cost"],
                    currency=delivery_result["currency"],
                    estimated_delivery_time=delivery_info["estimated_delivery_time"],
                    reliability=delivery_info["reliability"],
                    reason=delivery_info["reason"]
                ),
                code_expires_in_minutes=SMS_CODE_EXPIRATION_MINUTES,
                can_resend_in_seconds=60,  # From constants
                attempts_remaining=2,  # Example - should come from rate limiting
                daily_limit_remaining=95,  # Example - should come from user limits
                verification_id=delivery_result.get("message_id"),
                next_steps=[
                    "Enter the verification code you received",
                    "Code expires in 5 minutes",
                    "Contact support if you don't receive the code"
                ]
            )
        
        except Exception as e:
            logger.error(f"SMS verification failed for {request.phone}: {str(e)}")
            return SMSVerificationResponse(
                success=False,
                message=f"Failed to send SMS: {str(e)}",
                phone=request.phone,
                delivery_info=SMSDeliveryInfo(
                    method=SMSDeliveryMethod.EXTERNAL_SMS,
                    provider="Unknown",
                    cost=0.0,
                    currency="UZS",
                    estimated_delivery_time="N/A",
                    reliability="unknown",
                    reason="Delivery failed"
                ),
                code_expires_in_minutes=0,
                can_resend_in_seconds=60,
                attempts_remaining=0,
                daily_limit_remaining=0,
                next_steps=["Please try again or contact support"]
            )
    
    async def send_bulk_sms(self, request: BulkSMSRequest) -> BulkSMSResponse:
        """Send SMS to multiple phone numbers."""
        start_time = datetime.now()
        successful_phones = []
        failed_phones = []
        total_cost = 0.0
        telegram_sends = 0
        external_sends = 0
        
        for phone in request.phones:
            try:
                # Check if user exists in Telegram (this would be a database query)
                user_exists_in_telegram = await self._check_telegram_user_exists(phone)
                
                # Create individual SMS request
                sms_request = SMSVerificationRequest(
                    phone=phone,
                    purpose=request.purpose,
                    check_telegram_existence=request.check_telegram_existence
                )
                
                # Send SMS
                response = await self.send_verification_sms(sms_request, user_exists_in_telegram)
                
                if response.success:
                    successful_phones.append(phone)
                    total_cost += response.delivery_info.cost
                    
                    if response.delivery_info.method == SMSDeliveryMethod.TELEGRAM_BOT:
                        telegram_sends += 1
                    else:
                        external_sends += 1
                else:
                    failed_phones.append({
                        "phone": phone,
                        "error": response.message
                    })
            
            except Exception as e:
                failed_phones.append({
                    "phone": phone,
                    "error": str(e)
                })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return BulkSMSResponse(
            total_phones=len(request.phones),
            successful_sends=len(successful_phones),
            failed_sends=len(failed_phones),
            total_cost=total_cost,
            cost_currency=SMS_SERVICE_CONFIG["currency"],
            telegram_sends=telegram_sends,
            external_sends=external_sends,
            successful_phones=successful_phones,
            failed_phones=failed_phones,
            processing_time_seconds=processing_time,
            estimated_delivery_time="1-3 minutes"
        )
    
    async def _send_sms_with_fallback(self, phone: str, message: str, preferred_method: SMSDeliveryMethod, purpose: SMSCodePurpose) -> Dict[str, Any]:
        """Send SMS with fallback logic."""
        
        # Try preferred method first
        if preferred_method == SMSDeliveryMethod.TELEGRAM_BOT and self.telegram_service:
            try:
                return await self.telegram_service.send_sms(phone, message)
            except Exception as e:
                logger.warning(f"Telegram SMS failed for {phone}, falling back to external: {str(e)}")
                # Fall back to external SMS
                if self.external_service:
                    return await self.external_service.send_sms(phone, message)
                else:
                    raise SMSDeliveryError("No fallback SMS service available")
        
        elif preferred_method == SMSDeliveryMethod.EXTERNAL_SMS and self.external_service:
            return await self.external_service.send_sms(phone, message)
        
        else:
            raise SMSDeliveryError(f"No SMS service available for method: {preferred_method}")
    
    async def _check_telegram_user_exists(self, phone: str) -> bool:
        """Check if user exists in Telegram database."""
        # This would typically query your database
        # Implementation depends on your database structure
        
        # Example implementation:
        # normalized_phone = normalize_phone_for_comparison(phone)
        # user = await db.query("SELECT id FROM users WHERE phone = ? AND telegram_user_id IS NOT NULL", normalized_phone)
        # return user is not None
        
        return False  # Placeholder - implement based on your database
    
    def _update_stats(self, delivery_result: Dict[str, Any]):
        """Update SMS delivery statistics."""
        self.stats["total_sms_sent"] += 1
        self.stats["total_cost"] += delivery_result.get("cost", 0.0)
        
        if delivery_result["delivery_method"] == SMSDeliveryMethod.TELEGRAM_BOT:
            self.stats["telegram_deliveries"] += 1
        else:
            self.stats["external_deliveries"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get SMS service statistics."""
        return self.stats.copy()
    
    async def check_delivery_status(self, message_id: str, delivery_method: SMSDeliveryMethod) -> Dict[str, Any]:
        """Check delivery status of sent SMS."""
        if delivery_method == SMSDeliveryMethod.TELEGRAM_BOT and self.telegram_service:
            return await self.telegram_service.check_delivery_status(message_id)
        elif delivery_method == SMSDeliveryMethod.EXTERNAL_SMS and self.external_service:
            return await self.external_service.check_delivery_status(message_id)
        else:
            return {"status": "unknown", "provider": "Unknown"}

# Factory function for easy service creation
def create_sms_service(telegram_config: Dict[str, Any] = None, external_config: Dict[str, Any] = None) -> SMSService:
    """Create SMS service with provided configurations."""
    return SMSService(telegram_config, external_config)

class SMSWorkflowManager:
    """Manages SMS verification workflows with retry logic and admin override."""
    
    def __init__(self):
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
        self.telegram_provider = TelegramSMSService(None)
        self.external_provider = ExternalSMSService(None)
    
    async def start_verification_workflow(
        self, 
        request: SMSVerificationWorkflowRequest
    ) -> SMSVerificationWorkflowResponse:
        """Start a new SMS verification workflow."""
        
        workflow_id = f"wf_{uuid.uuid4().hex[:12]}"
        
        # Create workflow record
        workflow = {
            "id": workflow_id,
            "phone_number": request.phone_number,
            "user_id": request.user_id,
            "purpose": request.purpose,
            "status": SMSVerificationWorkflowStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(
                minutes=SMS_VERIFICATION_WORKFLOW["user_confirmation_timeout_minutes"]
            ),
            "attempt_count": 0,
            "max_attempts": SMS_VERIFICATION_WORKFLOW["max_retry_attempts"],
            "delivery_history": [],
            "last_error": None,
            "preferred_language": request.preferred_language or "en"
        }
        
        self.active_workflows[workflow_id] = workflow
        
        # Attempt to send SMS
        delivery_result = await self._attempt_sms_delivery(workflow_id)
        
        return self._build_workflow_response(workflow_id, delivery_result)
    
    async def _attempt_sms_delivery(self, workflow_id: str) -> Dict[str, Any]:
        """Attempt to deliver SMS using dual delivery logic."""
        
        workflow = self.active_workflows[workflow_id]
        workflow["attempt_count"] += 1
        workflow["updated_at"] = datetime.utcnow()
        
        phone_number = workflow["phone_number"]
        purpose = workflow["purpose"]
        
        # Generate verification code
        verification_code = self._generate_verification_code()
        workflow["current_code"] = verification_code
        workflow["code_expires_at"] = datetime.utcnow() + timedelta(
            minutes=SMS_CODE_EXPIRATION_MINUTES
        )
        
        # Try Telegram delivery first (free)
        telegram_result = await self._try_telegram_delivery(
            phone_number, verification_code, purpose
        )
        
        delivery_result = {
            "success": False,
            "delivery_method": None,
            "delivery_status": SMSDeliveryStatus.FAILED,
            "message": "",
            "error": None
        }
        
        if telegram_result["success"]:
            # Telegram delivery successful
            delivery_result.update({
                "success": True,
                "delivery_method": SMSDeliveryMethod.TELEGRAM_BOT,
                "delivery_status": SMSDeliveryStatus.SENT,
                "message": "SMS sent via Telegram. Please check your Telegram messages.",
                "cost": 0
            })
            workflow["status"] = SMSVerificationWorkflowStatus.PENDING
        else:
            # Try external SMS service
            external_result = await self._try_external_delivery(
                phone_number, verification_code, purpose, workflow["preferred_language"]
            )
            
            if external_result["success"]:
                # External SMS successful
                delivery_result.update({
                    "success": True,
                    "delivery_method": SMSDeliveryMethod.EXTERNAL_SMS,
                    "delivery_status": SMSDeliveryStatus.SENT,
                    "message": "SMS sent to your phone. Please check your messages.",
                    "cost": SMS_SERVICE_CONFIG["cost_per_sms"]
                })
                workflow["status"] = SMSVerificationWorkflowStatus.PENDING
            else:
                # Both methods failed
                delivery_result.update({
                    "success": False,
                    "delivery_method": SMSDeliveryMethod.FALLBACK,
                    "delivery_status": SMSDeliveryStatus.FAILED,
                    "message": "Failed to send SMS. Please confirm if you want to retry.",
                    "error": external_result.get("error", "Unknown error"),
                    "cost": 0
                })
                workflow["status"] = SMSVerificationWorkflowStatus.AWAITING_CONFIRMATION
                workflow["last_error"] = delivery_result["error"]
        
        # Record delivery attempt
        workflow["delivery_history"].append({
            "attempt": workflow["attempt_count"],
            "timestamp": datetime.utcnow().isoformat(),
            "telegram_result": telegram_result,
            "external_result": external_result if not telegram_result["success"] else None,
            "final_result": delivery_result
        })
        
        return delivery_result
    
    async def _try_telegram_delivery(
        self, 
        phone_number: str, 
        code: str, 
        purpose: SMSCodePurpose
    ) -> Dict[str, Any]:
        """Try to deliver SMS via Telegram bot."""
        try:
            # Check if user exists in Telegram database
            telegram_user = await self._find_telegram_user_by_phone(phone_number)
            
            if telegram_user:
                # Send via Telegram bot
                result = await self.telegram_provider.send_sms(
                    SMSVerificationRequest(
                        phone_number=phone_number,
                        code=code,
                        purpose=purpose,
                        delivery_method=SMSDeliveryMethod.TELEGRAM_BOT
                    )
                )
                return {
                    "success": result.delivery_status == SMSDeliveryStatus.SENT,
                    "telegram_user_id": telegram_user.get("telegram_id"),
                    "message": result.message,
                    "error": None if result.delivery_status == SMSDeliveryStatus.SENT else result.message
                }
            else:
                return {
                    "success": False,
                    "telegram_user_id": None,
                    "message": "User not found in Telegram database",
                    "error": "telegram_user_not_found"
                }
        
        except Exception as e:
            return {
                "success": False,
                "telegram_user_id": None,
                "message": f"Telegram delivery failed: {str(e)}",
                "error": str(e)
            }
    
    async def _try_external_delivery(
        self, 
        phone_number: str, 
        code: str, 
        purpose: SMSCodePurpose,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Try to deliver SMS via external SMS service."""
        try:
            result = await self.external_provider.send_sms(
                SMSVerificationRequest(
                    phone_number=phone_number,
                    code=code,
                    purpose=purpose,
                    delivery_method=SMSDeliveryMethod.EXTERNAL_SMS,
                    language=language
                )
            )
            return {
                "success": result.delivery_status == SMSDeliveryStatus.SENT,
                "provider": "eskiz.uz",
                "message": result.message,
                "cost": SMS_SERVICE_CONFIG["cost_per_sms"],
                "error": None if result.delivery_status == SMSDeliveryStatus.SENT else result.message
            }
        
        except Exception as e:
            return {
                "success": False,
                "provider": "eskiz.uz",
                "message": f"External SMS delivery failed: {str(e)}",
                "cost": 0,
                "error": str(e)
            }
    
    async def handle_user_confirmation(
        self, 
        request: SMSVerificationConfirmationRequest
    ) -> SMSVerificationWorkflowResponse:
        """Handle user confirmation after SMS delivery failure."""
        
        workflow_id = request.workflow_id
        if workflow_id not in self.active_workflows:
            raise ValueError("Workflow not found or expired")
        
        workflow = self.active_workflows[workflow_id]
        
        # Check if workflow is in correct state
        if workflow["status"] != SMSVerificationWorkflowStatus.AWAITING_CONFIRMATION:
            raise ValueError("Workflow is not awaiting confirmation")
        
        # Check if workflow has expired
        if datetime.utcnow() > workflow["expires_at"]:
            workflow["status"] = SMSVerificationWorkflowStatus.DISCARDED
            return self._build_workflow_response(workflow_id, {
                "success": False,
                "message": "Confirmation timeout. Please start verification again.",
                "error": "timeout"
            })
        
        if request.user_confirmed:
            # User wants to retry
            if workflow["attempt_count"] >= workflow["max_attempts"]:
                # Max attempts reached, require admin intervention
                workflow["status"] = SMSVerificationWorkflowStatus.ADMIN_REVIEW
                return self._build_workflow_response(workflow_id, {
                    "success": False,
                    "message": "Maximum retry attempts reached. Admin review required.",
                    "admin_contact_required": True
                })
            else:
                # Schedule retry
                workflow["status"] = SMSVerificationWorkflowStatus.RETRY_SCHEDULED
                
                # Wait for cooldown period
                cooldown_seconds = SMS_VERIFICATION_WORKFLOW["retry_cooldown_minutes"] * 60
                await asyncio.sleep(cooldown_seconds)
                
                # Attempt retry
                delivery_result = await self._attempt_sms_delivery(workflow_id)
                return self._build_workflow_response(workflow_id, delivery_result)
        else:
            # User doesn't want to retry
            workflow["status"] = SMSVerificationWorkflowStatus.DISCARDED
            return self._build_workflow_response(workflow_id, {
                "success": False,
                "message": "Verification cancelled by user.",
                "error": "user_cancelled"
            })
    
    async def handle_admin_verification(
        self, 
        request: AdminVerificationRequest
    ) -> AdminVerificationResponse:
        """Handle admin manual verification."""
        
        workflow_id = request.workflow_id
        if workflow_id not in self.active_workflows:
            raise ValueError("Workflow not found")
        
        workflow = self.active_workflows[workflow_id]
        
        response = AdminVerificationResponse(
            workflow_id=workflow_id,
            status="",
            action_taken=request.action,
            verified=False,
            message="",
            admin_id=request.admin_id,
            timestamp=datetime.utcnow()
        )
        
        if request.action == AdminVerificationAction.MANUAL_VERIFY:
            workflow["status"] = SMSVerificationWorkflowStatus.ADMIN_VERIFIED
            workflow["verified_by_admin"] = request.admin_id
            workflow["admin_notes"] = request.notes
            workflow["verification_method"] = request.verification_method
            
            response.status = "admin_verified"
            response.verified = True
            response.message = "Phone number manually verified by admin"
        
        elif request.action == AdminVerificationAction.MARK_INVALID:
            workflow["status"] = SMSVerificationWorkflowStatus.FAILED_FINAL
            workflow["marked_invalid_by"] = request.admin_id
            workflow["admin_notes"] = request.notes
            
            response.status = "failed_final"
            response.verified = False
            response.message = "Phone number marked as invalid by admin"
        
        elif request.action == AdminVerificationAction.REQUEST_ALTERNATIVE:
            workflow["status"] = SMSVerificationWorkflowStatus.ADMIN_REVIEW
            workflow["alternative_requested"] = True
            workflow["admin_notes"] = request.notes
            
            response.status = "admin_review"
            response.verified = False
            response.message = "Alternative contact method requested"
        
        workflow["updated_at"] = datetime.utcnow()
        
        return response
    
    def get_workflow_status(self, workflow_id: str) -> SMSWorkflowStatusResponse:
        """Get current status of a workflow."""
        
        if workflow_id not in self.active_workflows:
            raise ValueError("Workflow not found")
        
        workflow = self.active_workflows[workflow_id]
        
        return SMSWorkflowStatusResponse(
            workflow_id=workflow_id,
            status=workflow["status"],
            phone_number=workflow["phone_number"],
            created_at=workflow["created_at"],
            updated_at=workflow["updated_at"],
            expires_at=workflow.get("expires_at"),
            attempt_count=workflow["attempt_count"],
            max_attempts=workflow["max_attempts"],
            last_error=workflow.get("last_error"),
            delivery_history=workflow["delivery_history"]
        )
    
    def _build_workflow_response(
        self, 
        workflow_id: str, 
        delivery_result: Dict[str, Any]
    ) -> SMSVerificationWorkflowResponse:
        """Build workflow response from delivery result."""
        
        workflow = self.active_workflows[workflow_id]
        
        # Determine next action and retry availability
        next_action = None
        retry_available = False
        retry_cooldown_seconds = None
        admin_contact_required = False
        
        if workflow["status"] == SMSVerificationWorkflowStatus.PENDING:
            next_action = "enter_code"
        elif workflow["status"] == SMSVerificationWorkflowStatus.AWAITING_CONFIRMATION:
            next_action = "confirm_retry"
            retry_available = workflow["attempt_count"] < workflow["max_attempts"]
        elif workflow["status"] == SMSVerificationWorkflowStatus.RETRY_SCHEDULED:
            next_action = "wait_for_retry"
            retry_cooldown_seconds = SMS_VERIFICATION_WORKFLOW["retry_cooldown_minutes"] * 60
        elif workflow["status"] == SMSVerificationWorkflowStatus.ADMIN_REVIEW:
            next_action = "contact_admin"
            admin_contact_required = True
        
        return SMSVerificationWorkflowResponse(
            workflow_id=workflow_id,
            status=workflow["status"],
            phone_number=workflow["phone_number"],
            delivery_method=delivery_result.get("delivery_method", SMSDeliveryMethod.FALLBACK),
            delivery_status=delivery_result.get("delivery_status", SMSDeliveryStatus.FAILED),
            message=delivery_result.get("message", "Unknown status"),
            next_action=next_action,
            retry_available=retry_available,
            retry_cooldown_seconds=retry_cooldown_seconds,
            admin_contact_required=admin_contact_required,
            expires_at=workflow.get("expires_at")
        )
    
    def _generate_verification_code(self) -> str:
        """Generate a random verification code."""
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(SMS_CODE_LENGTH)])
    
    async def _find_telegram_user_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Find Telegram user by phone number (mock implementation)."""
        # This would query the actual Telegram user database
        # For now, return None to simulate user not found
        return None
    
    def cleanup_expired_workflows(self):
        """Clean up expired workflows."""
        current_time = datetime.utcnow()
        expired_workflows = []
        
        for workflow_id, workflow in self.active_workflows.items():
            if workflow.get("expires_at") and current_time > workflow["expires_at"]:
                expired_workflows.append(workflow_id)
        
        for workflow_id in expired_workflows:
            self.active_workflows[workflow_id]["status"] = SMSVerificationWorkflowStatus.DISCARDED
            # Could move to archive instead of deleting
            del self.active_workflows[workflow_id] 