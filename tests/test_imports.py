"""
Test that all modules and components can be imported successfully.
This is crucial for a shared library to ensure no circular dependencies or import errors.
"""

def test_main_package_import():
    """Test that the main package can be imported."""
    import saytoai_shared
    assert saytoai_shared.__version__ == "0.0.1"


def test_constants_import():
    """Test that constants module imports successfully."""
    from saytoai_shared import constants
    from saytoai_shared.constants import (
        SERVICE_TIERS,
        INITIAL_FREE_CREDITS,
        UserRole,
        PaymentStatus,
        SubscriptionType,
        AuthMethod,
        EmailCodePurpose
    )
    
    # Verify constants are accessible
    assert constants.SERVICE_TIERS is not None
    assert isinstance(INITIAL_FREE_CREDITS, int)
    assert UserRole.USER.value == "user"


def test_utils_import():
    """Test that utils module imports successfully."""
    from saytoai_shared import utils
    from saytoai_shared.utils import (
        sanitize_username,
        validate_phone_number,
        generate_order_id,
        generate_payment_order_id,
        get_display_name
    )
    
    # Verify functions are callable
    assert callable(sanitize_username)
    assert callable(validate_phone_number)
    assert callable(generate_order_id)


def test_user_schemas_import():
    """Test that user schemas import successfully."""
    from saytoai_shared.schemas import user
    from saytoai_shared.schemas.user import (
        UserProfile,
        UserPreferences,
        UserCredits,
        UserSubscription,
        UserAuthentication,
        UserProfileCreate,
        UserProfileUpdate
    )
    
    # Verify classes are available
    assert UserProfile is not None
    assert UserPreferences is not None
    assert UserCredits is not None


def test_auth_schemas_import():
    """Test that auth schemas import successfully."""
    from saytoai_shared.schemas import auth
    from saytoai_shared.schemas.auth import (
        RegistrationRequest,
        LoginRequest,
        EmailVerificationRequest,
        AuthToken,
        UserSession
    )
    
    # Verify classes are available
    assert RegistrationRequest is not None
    assert LoginRequest is not None
    assert AuthToken is not None


def test_payment_schemas_import():
    """Test that payment schemas import successfully."""
    from saytoai_shared.schemas import payments
    from saytoai_shared.schemas.payments import (
        PaymentRequest,
        PaymentResponse,
        PaymentTransaction,
        PaymentProvider,
        PaymentMethod
    )
    
    # Verify classes and enums are available
    assert PaymentRequest is not None
    assert PaymentResponse is not None
    assert PaymentProvider.PAYME.value == "payme"


def test_sms_schemas_import():
    """Test that SMS schemas import successfully."""
    from saytoai_shared.schemas import sms
    from saytoai_shared.schemas.sms import (
        SMSVerificationRequest,
        SMSCodeVerificationRequest,
        SMSVerificationCode,
        SMSDeliveryMethod,
        SMSCodePurpose
    )
    
    # Verify classes and enums are available
    assert SMSVerificationRequest is not None
    assert SMSDeliveryMethod.TELEGRAM_BOT.value == "telegram_bot"
    assert SMSCodePurpose.REGISTRATION.value == "registration"


def test_service_schemas_import():
    """Test that service schemas import successfully."""
    from saytoai_shared.schemas import service
    from saytoai_shared.schemas.service import (
        ServiceAccess,
        PaymentInfo,
        AudioSession,
        ServiceStatus,
        SystemMetrics
    )
    
    # Verify classes are available
    assert ServiceAccess is not None
    assert PaymentInfo is not None
    assert AudioSession is not None


def test_roles_schemas_import():
    """Test that roles schemas import successfully."""
    from saytoai_shared.schemas import roles
    from saytoai_shared.schemas.roles import (
        CustomPrompt,
        UserRoleDefinition,
        PromptContext,
        RolePermission
    )
    
    # Verify classes and enums are available
    assert CustomPrompt is not None
    assert PromptContext.DEVELOPER.value == "developer"
    assert RolePermission.USE_BASIC_FEATURES.value == "use_basic_features"


def test_fraud_prevention_schemas_import():
    """Test that fraud prevention schemas import successfully."""
    from saytoai_shared.schemas import fraud_prevention
    from saytoai_shared.schemas.fraud_prevention import (
        DeviceFingerprint,
        IPAnalysis,
        RiskAssessment,
        RegistrationAttempt
    )
    
    # Verify classes are available
    assert DeviceFingerprint is not None
    assert IPAnalysis is not None
    assert RiskAssessment is not None


def test_services_import():
    """Test that services module imports successfully."""
    from saytoai_shared.services import sms_service
    from saytoai_shared.services.sms_service import (
        SMSService,
        SMSWorkflowManager,
        create_sms_service
    )
    
    # Verify classes and functions are available
    assert SMSService is not None
    assert SMSWorkflowManager is not None
    assert callable(create_sms_service)


def test_prompts_import():
    """Test that prompts module imports successfully."""
    from saytoai_shared import prompts
    from saytoai_shared.prompts import (
        DEVELOPER_PROMPT,
        DESIGNER_PROMPT,
        AI_CHAT_PROMPT
    )
    
    # Verify prompts are strings
    assert isinstance(DEVELOPER_PROMPT, str)
    assert isinstance(DESIGNER_PROMPT, str)
    assert isinstance(AI_CHAT_PROMPT, str)
    assert len(DEVELOPER_PROMPT) > 0


def test_package_level_imports():
    """Test that main package exports work correctly."""
    from saytoai_shared import (
        UserProfile,
        SERVICE_TIERS,
        sanitize_username,
        PaymentStatus,
        SubscriptionType
    )
    
    # Verify main exports are accessible
    assert UserProfile is not None
    assert SERVICE_TIERS is not None
    assert callable(sanitize_username)
    assert PaymentStatus.PENDING.value == "pending"
    assert SubscriptionType.FREE_TRIAL.value == "free"


def test_no_circular_imports():
    """Test that there are no circular import issues."""
    # Import all main modules in sequence
    import saytoai_shared.constants
    import saytoai_shared.utils
    import saytoai_shared.prompts
    import saytoai_shared.schemas.user
    import saytoai_shared.schemas.auth
    import saytoai_shared.schemas.payments
    import saytoai_shared.schemas.sms
    import saytoai_shared.schemas.service
    import saytoai_shared.schemas.roles
    import saytoai_shared.schemas.fraud_prevention
    import saytoai_shared.services.sms_service
    
    # If we get here without errors, no circular imports exist
    assert True


def test_pydantic_models_instantiation():
    """Test that Pydantic models can be instantiated."""
    from saytoai_shared.schemas.user import UserProfile
    from saytoai_shared.schemas.auth import RegistrationRequest
    from saytoai_shared.schemas.payments import PaymentRequest
    from decimal import Decimal
    
    # Test UserProfile
    user = UserProfile(user_id=1, username="test")
    assert user.user_id == 1
    
    # Test RegistrationRequest
    reg = RegistrationRequest(
        email="test@gmail.com",
        password="password123"
    )
    assert reg.email == "test@gmail.com"
    
    # Test PaymentRequest
    payment = PaymentRequest(
        amount=Decimal("50000"),
        order_id="test_order",
        description="Test payment",
        user_id="123",
        credits_purchased=100,
        payment_method="payme"
    )
    assert payment.amount == Decimal("50000")


def test_enum_values():
    """Test that all enums have expected values."""
    from saytoai_shared.constants import (
        UserRole,
        PaymentStatus,
        SubscriptionType,
        AuthMethod,
        EmailCodePurpose
    )
    from saytoai_shared.schemas.payments import PaymentProvider
    from saytoai_shared.schemas.sms import SMSDeliveryMethod
    
    # Test enum values
    assert UserRole.USER.value == "user"
    assert UserRole.ADMIN.value == "admin"
    assert PaymentStatus.PENDING.value == "pending"
    assert PaymentStatus.COMPLETED.value == "completed"
    assert SubscriptionType.FREE_TRIAL.value == "free"
    assert AuthMethod.EMAIL.value == "email"
    assert PaymentProvider.PAYME.value == "payme"
    assert SMSDeliveryMethod.TELEGRAM_BOT.value == "telegram_bot" 