"""
SMS service for sending verification codes
"""
import random
from typing import Optional
from app.core.config import settings


class SMSService:
    """Service for sending SMS messages"""
    
    def __init__(self):
        self.provider = settings.SMS_PROVIDER
        self.api_key = settings.SMS_API_KEY
    
    def send_verification_code(self, phone: str) -> str:
        """
        Send verification code to phone
        
        Args:
            phone: Phone number
            
        Returns:
            Verification code
        """
        # Generate 6-digit code
        code = str(random.randint(100000, 999999))
        
        if self.provider == "test":
            # For testing - just print to console
            print(f"[SMS] Код подтверждения для {phone}: {code}")
            return code
        
        # TODO: Implement real SMS provider integration
        # Example providers: SMS.ru, SMSC.ru, Twilio, etc.
        
        return code
    
    def send_message(self, phone: str, message: str) -> bool:
        """
        Send SMS message
        
        Args:
            phone: Phone number
            message: Message text
            
        Returns:
            True if sent successfully
        """
        if self.provider == "test":
            print(f"[SMS] Сообщение для {phone}: {message}")
            return True
        
        # TODO: Implement real SMS provider integration
        
        return True


# Singleton instance
sms_service = SMSService()
