import os
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv

load_dotenv()


class SendGridEmailService:
    """Service for sending emails via SendGrid API"""
    
    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@expensetracker.com")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # Initialize SendGrid client if API key is available
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None
        
    def send_otp_email(self, to_email: str, otp: str, name: Optional[str] = None) -> bool:
        """
        Send OTP verification email via SendGrid
        
        Args:
            to_email: Recipient email address
            otp: One-time password code
            name: Optional recipient name
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.client:
            # In development, print OTP to console if SendGrid not configured
            print(f"[DEV MODE] OTP for {to_email}: {otp}")
            print("ℹ️  Configure SENDGRID_API_KEY to send real emails")
            return True
            
        try:
            # Email content
            greeting = f"Hi {name}," if name else "Hi,"
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4F46E5;">Email Verification</h2>
                        <p>{greeting}</p>
                        <p>Thank you for registering! Please use the following OTP code to verify your email address:</p>
                        <div style="background-color: #F3F4F6; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                            <h1 style="color: #4F46E5; letter-spacing: 8px; margin: 0; font-size: 32px;">{otp}</h1>
                        </div>
                        <p>This code will expire in <strong>10 minutes</strong>.</p>
                        <p style="color: #6B7280; font-size: 14px; margin-top: 30px;">
                            If you didn't request this code, please ignore this email.
                        </p>
                        <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
                        <p style="color: #6B7280; font-size: 12px;">
                            Best regards,<br>
                            Expense Tracker Team
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Create email message
            message = Mail(
                from_email=Email(self.from_email, "Expense Tracker"),
                to_emails=To(to_email),
                subject="Email Verification - OTP Code",
                html_content=Content("text/html", html_content)
            )
            
            # Send email
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ OTP email sent successfully to {to_email}")
                return True
            else:
                print(f"⚠️  SendGrid returned status code: {response.status_code}")
                print(f"[DEV MODE] OTP for {to_email}: {otp}")
                return False
            
        except Exception as e:
            print(f"❌ Error sending email via SendGrid: {e}")
            # Fallback: print OTP to console
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
        registration_link = f"{self.frontend_url}/register?invitation={invitation_token}"
        
        if not self.client:
            print(f"[DEV MODE] Friend invitation for {to_email}")
            print(f"From: {inviter_name}")
            print(f"Registration link: {registration_link}")
            return True
            
        try:
            # Email content
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4F46E5;">You're Invited!</h2>
                        <p>Hi there!</p>
                        <p><strong>{inviter_name}</strong> has invited you to join Expense Tracker to manage shared expenses together!</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{registration_link}" 
                               style="background-color: #4F46E5; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 6px; display: inline-block;
                                      font-weight: bold;">
                                Accept Invitation
                            </a>
                        </div>
                        <p style="font-size: 14px; color: #6B7280;">
                            Or copy and paste this link into your browser:<br>
                            <a href="{registration_link}" style="color: #4F46E5; word-break: break-all;">{registration_link}</a>
                        </p>
                        <p style="color: #6B7280; font-size: 14px;">
                            This invitation will expire in 7 days.
                        </p>
                        <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
                        <p style="color: #6B7280; font-size: 12px;">
                            If you didn't expect this invitation, you can safely ignore this email.<br><br>
                            Best regards,<br>
                            Expense Tracker Team
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Create email message
            message = Mail(
                from_email=Email(self.from_email, "Expense Tracker"),
                to_emails=To(to_email),
                subject=f"{inviter_name} invited you to join Expense Tracker!",
                html_content=Content("text/html", html_content)
            )
            
            # Send email
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Invitation email sent successfully to {to_email}")
                return True
            else:
                print(f"⚠️  SendGrid returned status code: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"❌ Error sending invitation via SendGrid: {e}")
            print(f"[DEV MODE] Friend invitation for {to_email}")
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
        if not self.client:
            print(f"[DEV MODE] Friend request notification for {to_email}")
            print(f"{requester_name} added you as a friend")
            return True
            
        try:
            greeting = f"Hi {to_name}," if to_name else "Hi,"
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4F46E5;">New Friend Request!</h2>
                        <p>{greeting}</p>
                        <p>Great news! <strong>{requester_name}</strong> has added you as a friend on Expense Tracker.</p>
                        <p>You can now share and track expenses with {requester_name}.</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{self.frontend_url}/login" 
                               style="background-color: #4F46E5; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 6px; display: inline-block;
                                      font-weight: bold;">
                                Login to Your Account
                            </a>
                        </div>
                        <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
                        <p style="color: #6B7280; font-size: 12px;">
                            Best regards,<br>
                            Expense Tracker Team
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Create email message
            message = Mail(
                from_email=Email(self.from_email, "Expense Tracker"),
                to_emails=To(to_email),
                subject=f"{requester_name} added you as a friend on Expense Tracker",
                html_content=Content("text/html", html_content)
            )
            
            # Send email
            response = self.client.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Friend notification sent successfully to {to_email}")
                return True
            else:
                print(f"⚠️  SendGrid returned status code: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"❌ Error sending notification via SendGrid: {e}")
            return False


# Global instance
email_service = SendGridEmailService()

