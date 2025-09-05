"""
Authentication tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.auth import OTPLog
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService


class TestAuthAPI:
    """Test authentication API endpoints"""
    
    def test_request_otp_success(self, client: TestClient, db_session: Session):
        """Test successful OTP request"""
        response = client.post(
            "/api/v1/auth/request-otp",
            json={"phone": "+1234567890"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "OTP sent successfully"
        assert "otp_id" in data
    
    def test_request_otp_invalid_phone(self, client: TestClient):
        """Test OTP request with invalid phone"""
        response = client.post(
            "/api/v1/auth/request-otp",
            json={"phone": "invalid_phone"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_verify_otp_success(self, client: TestClient, db_session: Session):
        """Test successful OTP verification"""
        # First request OTP
        otp_response = client.post(
            "/api/v1/auth/request-otp",
            json={"phone": "+1234567890"}
        )
        assert otp_response.status_code == 200
        
        # Get OTP from database (in real scenario, this would come from SMS)
        otp_log = db_session.query(OTPLog).filter(
            OTPLog.phone == "+1234567890"
        ).first()
        
        # Verify OTP
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={
                "phone": "+1234567890",
                "otp": otp_log.otp_code,
                "device_info": "test_device"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["is_new_user"] is True
        assert "auth_token" in data
    
    def test_verify_otp_invalid(self, client: TestClient):
        """Test OTP verification with invalid OTP"""
        response = client.post(
            "/api/v1/auth/verify-otp",
            json={
                "phone": "+1234567890",
                "otp": "000000",
                "device_info": "test_device"
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Invalid or expired OTP"
    
    def test_complete_profile_success(self, client: TestClient, db_session: Session):
        """Test successful profile completion"""
        # First get auth token
        otp_response = client.post(
            "/api/v1/auth/request-otp",
            json={"phone": "+1234567890"}
        )
        
        otp_log = db_session.query(OTPLog).filter(
            OTPLog.phone == "+1234567890"
        ).first()
        
        verify_response = client.post(
            "/api/v1/auth/verify-otp",
            json={
                "phone": "+1234567890",
                "otp": otp_log.otp_code,
                "device_info": "test_device"
            }
        )
        
        auth_token = verify_response.json()["auth_token"]
        
        # Complete profile
        response = client.post(
            "/api/v1/auth/complete-profile",
            json={
                "auth_token": auth_token,
                "full_name": "Test User",
                "gender": "male"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["user"]["full_name"] == "Test User"
        assert data["user"]["gender"] == "male"
    
    def test_logout_success(self, client: TestClient, db_session: Session):
        """Test successful logout"""
        # First get auth token
        otp_response = client.post(
            "/api/v1/auth/request-otp",
            json={"phone": "+1234567890"}
        )
        
        otp_log = db_session.query(OTPLog).filter(
            OTPLog.phone == "+1234567890"
        ).first()
        
        verify_response = client.post(
            "/api/v1/auth/verify-otp",
            json={
                "phone": "+1234567890",
                "otp": otp_log.otp_code,
                "device_info": "test_device"
            }
        )
        
        auth_token = verify_response.json()["auth_token"]
        
        # Logout
        response = client.post(
            "/api/v1/auth/logout",
            json={"auth_token": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestAuthService:
    """Test authentication service"""
    
    def test_create_user(self, db_session: Session):
        """Test user creation"""
        auth_service = AuthService()
        user = auth_service.create_user(db_session, "+1234567890")
        
        assert user.phone == "+1234567890"
        assert user.phone_verified is True
        assert user.is_active is True
    
    def test_get_user_by_phone(self, db_session: Session):
        """Test getting user by phone"""
        auth_service = AuthService()
        
        # Create user
        user = auth_service.create_user(db_session, "+1234567890")
        
        # Get user
        found_user = auth_service.get_user_by_phone(db_session, "+1234567890")
        
        assert found_user is not None
        assert found_user.user_id == user.user_id
    
    def test_create_session(self, db_session: Session):
        """Test session creation"""
        auth_service = AuthService()
        
        # Create user
        user = auth_service.create_user(db_session, "+1234567890")
        
        # Create session
        session = auth_service.create_session(
            db_session, 
            user.user_id, 
            "test_device"
        )
        
        assert session.user_id == user.user_id
        assert session.device_info == "test_device"
        assert session.auth_token is not None


class TestOTPService:
    """Test OTP service"""
    
    def test_create_otp_log(self, db_session: Session):
        """Test OTP log creation"""
        otp_service = OTPService()
        otp_log, otp_code = otp_service.create_otp_log(db_session, "+1234567890")
        
        assert otp_log.phone == "+1234567890"
        assert otp_log.otp_code == otp_code
        assert otp_log.is_verified is False
        assert len(otp_code) == 6
    
    def test_verify_otp_success(self, db_session: Session):
        """Test successful OTP verification"""
        otp_service = OTPService()
        
        # Create OTP
        otp_log, otp_code = otp_service.create_otp_log(db_session, "+1234567890")
        
        # Verify OTP
        verified_otp = otp_service.verify_otp(db_session, "+1234567890", otp_code)
        
        assert verified_otp is not None
        assert verified_otp.is_verified is True
    
    def test_verify_otp_invalid(self, db_session: Session):
        """Test invalid OTP verification"""
        otp_service = OTPService()
        
        # Create OTP
        otp_service.create_otp_log(db_session, "+1234567890")
        
        # Try to verify with wrong OTP
        verified_otp = otp_service.verify_otp(db_session, "+1234567890", "000000")
        
        assert verified_otp is None
