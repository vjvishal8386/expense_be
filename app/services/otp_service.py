import secrets
import time
from typing import Dict, Optional
from datetime import datetime, timedelta
from uuid import UUID


class OTPService:
    """Service for generating and verifying OTP codes"""
    
    def __init__(self):
        # In-memory storage for OTPs (use Redis in production)
        self._otp_storage: Dict[str, Dict] = {}
        self.otp_length = 6
        self.otp_expiry_minutes = 10
        
    def generate_otp(self, user_id: UUID, email: str) -> str:
        """
        Generate a 6-digit OTP for email verification
        
        Args:
            user_id: User's UUID
            email: User's email address
            
        Returns:
            str: 6-digit OTP code
        """
        # Generate random 6-digit OTP
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(self.otp_length)])
        
        # Store OTP with expiration time
        key = f"{user_id}:{email}"
        self._otp_storage[key] = {
            'otp': otp,
            'user_id': str(user_id),
            'email': email,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=self.otp_expiry_minutes),
            'attempts': 0
        }
        
        return otp
    
    def verify_otp(self, user_id: UUID, email: str, otp: str) -> bool:
        """
        Verify OTP code
        
        Args:
            user_id: User's UUID
            email: User's email address
            otp: OTP code to verify
            
        Returns:
            bool: True if OTP is valid, False otherwise
        """
        key = f"{user_id}:{email}"
        
        if key not in self._otp_storage:
            return False
        
        otp_data = self._otp_storage[key]
        
        # Check if OTP has expired
        if datetime.utcnow() > otp_data['expires_at']:
            del self._otp_storage[key]
            return False
        
        # Check if too many attempts (max 5 attempts)
        if otp_data['attempts'] >= 5:
            del self._otp_storage[key]
            return False
        
        # Increment attempts
        otp_data['attempts'] += 1
        
        # Verify OTP
        if otp_data['otp'] == otp:
            # OTP is valid, remove it
            del self._otp_storage[key]
            return True
        
        return False
    
    def get_otp(self, user_id: UUID, email: str) -> Optional[str]:
        """
        Get stored OTP (for resending)
        
        Args:
            user_id: User's UUID
            email: User's email address
            
        Returns:
            Optional[str]: OTP code if exists and not expired, None otherwise
        """
        key = f"{user_id}:{email}"
        
        if key not in self._otp_storage:
            return None
        
        otp_data = self._otp_storage[key]
        
        # Check if OTP has expired
        if datetime.utcnow() > otp_data['expires_at']:
            del self._otp_storage[key]
            return None
        
        return otp_data['otp']
    
    def delete_otp(self, user_id: UUID, email: str) -> None:
        """Delete OTP from storage"""
        key = f"{user_id}:{email}"
        if key in self._otp_storage:
            del self._otp_storage[key]
    
    def cleanup_expired_otps(self) -> None:
        """Clean up expired OTPs (call periodically)"""
        current_time = datetime.utcnow()
        expired_keys = [
            key for key, data in self._otp_storage.items()
            if current_time > data['expires_at']
        ]
        for key in expired_keys:
            del self._otp_storage[key]


# Global instance
otp_service = OTPService()

