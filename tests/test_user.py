"""
Tests for user schemas and related functionality.
"""

import pytest
from datetime import datetime
from saytoai_shared.schemas.user import (
    UserProfile, 
    UserPreferences, 
    UserCredits, 
    UserSubscription,
    UserAuthentication,
    UserProfileCreate,
    UserProfileUpdate
)
from saytoai_shared.constants import (
    SubscriptionType, 
    SubscriptionStatus,
    UserRole,
    AuthMethod
)


def test_user_profile_creation():
    """Test basic UserProfile creation."""
    user = UserProfile(
        user_id=12345,
        username="test_user",
        first_name="Test",
        last_name="User"
    )
    
    assert user.user_id == 12345
    assert user.username == "test_user"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.is_admin is False  # Default value


def test_user_profile_with_embedded_data():
    """Test UserProfile with embedded authentication and preferences."""
    auth = UserAuthentication(
        email="test@example.com",
        email_verified=True,
        auth_method=AuthMethod.EMAIL
    )
    
    preferences = UserPreferences(
        language="english",
        role=UserRole.USER,
        notifications_enabled=True
    )
    
    credits = UserCredits(
        remaining=50,
        total_used=10
    )
    
    user = UserProfile(
        user_id=12345,
        username="test_user",
        auth=auth,
        preferences=preferences,
        credits=credits
    )
    
    assert user.auth.email == "test@example.com"
    assert user.preferences.language == "english"
    assert user.credits.remaining == 50


def test_user_preferences_validation():
    """Test UserPreferences validation."""
    # Valid preferences
    prefs = UserPreferences(
        language="english",
        audio_language="auto",
        output_language="english"
    )
    
    assert prefs.language == "english"
    assert prefs.audio_language == "auto"
    
    # Test invalid language should raise validation error
    with pytest.raises(ValueError, match="Language must be one of"):
        UserPreferences(language="invalid_language")


def test_user_credits():
    """Test UserCredits model."""
    credits = UserCredits(
        remaining=100,
        total_used=50,
        daily_usage=5,
        monthly_usage=25
    )
    
    assert credits.remaining == 100
    assert credits.total_used == 50
    assert credits.daily_usage == 5
    assert credits.monthly_usage == 25


def test_user_subscription():
    """Test UserSubscription model."""
    subscription = UserSubscription(
        subscription_type=SubscriptionType.PREMIUM,
        status=SubscriptionStatus.ACTIVE,
        monthly_credit_limit=300
    )
    
    assert subscription.subscription_type == SubscriptionType.PREMIUM
    assert subscription.status == SubscriptionStatus.ACTIVE
    assert subscription.monthly_credit_limit == 300


def test_user_profile_create():
    """Test UserProfileCreate schema."""
    create_data = UserProfileCreate(
        email="newuser@example.com",
        password="securepassword123",
        first_name="New",
        last_name="User",
        language="english"
    )
    
    assert create_data.email == "newuser@example.com"
    assert create_data.password == "securepassword123"
    assert create_data.language == "english"


def test_user_profile_update():
    """Test UserProfileUpdate schema."""
    update_data = UserProfileUpdate(
        first_name="Updated",
        language="uzbek",
        notifications_enabled=False
    )
    
    assert update_data.first_name == "Updated"
    assert update_data.language == "uzbek"
    assert update_data.notifications_enabled is False


def test_user_authentication():
    """Test UserAuthentication model."""
    auth = UserAuthentication(
        email="user@example.com",
        email_verified=True,
        telegram_id=123456789,
        auth_method=AuthMethod.TELEGRAM,
        failed_login_attempts=0
    )
    
    assert auth.email == "user@example.com"
    assert auth.email_verified is True
    assert auth.telegram_id == 123456789
    assert auth.auth_method == AuthMethod.TELEGRAM
    assert auth.failed_login_attempts == 0


def test_enum_values():
    """Test that enums work correctly."""
    # Test SubscriptionType
    assert SubscriptionType.FREE_TRIAL.value == "free"
    assert SubscriptionType.PREMIUM.value == "premium"
    
    # Test UserRole
    assert UserRole.USER.value == "user"
    assert UserRole.ADMIN.value == "admin"
    
    # Test AuthMethod
    assert AuthMethod.EMAIL.value == "email"
    assert AuthMethod.TELEGRAM.value == "telegram"


def test_user_profile_json_serialization():
    """Test that UserProfile can be serialized to JSON."""
    user = UserProfile(
        user_id=12345,
        username="test_user",
        created_at=datetime.now()
    )
    
    # Should not raise an exception
    user_dict = user.dict()
    assert user_dict["user_id"] == 12345
    assert user_dict["username"] == "test_user"
    assert "created_at" in user_dict 