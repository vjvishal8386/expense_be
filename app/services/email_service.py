import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
    def send_otp_email(self, to_email: str, otp: str, name: Optional[str] = None) -> bool:
        """
        Send OTP verification email
        
        Args:
            to_email: Recipient email address
            otp: One-time password code
            name: Optional recipient name
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.smtp_username or not self.smtp_password:
            # In development, print OTP to console if SMTP not configured
            print(f"[DEV MODE] OTP for {to_email}: {otp}")
            return True
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = "Email Verification - OTP Code"
            
            # Email body
            greeting = f"Hi {name}," if name else "Hi,"
            body = f"""
{greeting}

Thank you for registering! Please use the following OTP code to verify your email address:

Your OTP Code: {otp}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Best regards,
Expense Tracker Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            # In development, still print OTP
            print(f"[DEV MODE] OTP for {to_email}: {otp}")
            return False
    
    def send_friend_invitation_email(
        self, 
        to_email: str, 
        inviter_name: str, 
        invitation_token: str
    ) -> bool:
        """
        Send friend invitation email with registration link
        
        Args:
            to_email: Recipient email address
            inviter_name: Name of the person sending the invitation
            invitation_token: Unique invitation token
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.smtp_username or not self.smtp_password:
            # In development, print invitation link to console
            registration_link = f"{self.frontend_url}/register?invitation={invitation_token}"
            print(f"[DEV MODE] Friend invitation for {to_email}")
            print(f"From: {inviter_name}")
            print(f"Registration link: {registration_link}")
            return True
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = f"{inviter_name} invited you to join Expense Tracker!"
            
            # Registration link
            registration_link = f"{self.frontend_url}/register?invitation={invitation_token}"
            
            # Email body
            body = f"""
Hi there!

{inviter_name} has invited you to join Expense Tracker to manage shared expenses together!

Click the link below to sign up and automatically become friends with {inviter_name}:

{registration_link}

This invitation will expire in 7 days.

If you didn't expect this invitation, you can safely ignore this email.

Best regards,
Expense Tracker Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending invitation email: {e}")
            # In development, still print link
            registration_link = f"{self.frontend_url}/register?invitation={invitation_token}"
            print(f"[DEV MODE] Friend invitation for {to_email}")
            print(f"From: {inviter_name}")
            print(f"Registration link: {registration_link}")
            return False
    
    def send_friend_request_notification(
        self, 
        to_email: str, 
        requester_name: str, 
        to_name: Optional[str] = None
    ) -> bool:
        """
        Send notification email when someone adds you as a friend
        
        Args:
            to_email: Recipient email address
            requester_name: Name of the person who added them as friend
            to_name: Optional recipient name
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.smtp_username or not self.smtp_password:
            # In development, print to console
            print(f"[DEV MODE] Friend request notification for {to_email}")
            print(f"{requester_name} added you as a friend")
            return True
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = f"{requester_name} added you as a friend on Expense Tracker"
            
            # Email body
            greeting = f"Hi {to_name}," if to_name else "Hi,"
            body = f"""
{greeting}

Great news! {requester_name} has added you as a friend on Expense Tracker.

You can now share and track expenses with {requester_name}.

Login to your account to start managing shared expenses:
{self.frontend_url}/login

Best regards,
Expense Tracker Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending friend request notification: {e}")
            return False


# Global instance
email_service = EmailService()

