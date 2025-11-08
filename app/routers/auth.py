from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models.user import User
from app.models.friend import Friend
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    OTPVerify, OTPResend, RegisterResponse
)
from app.security import verify_password, get_password_hash, create_access_token
from app.dependencies import get_current_user
from app.services.sendgrid_email_service import email_service
from app.services.otp_service import otp_service
from app.services.invitation_service import invitation_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="""
    Register a new user and send OTP for email verification.
    
    **Registration Flow:**
    1. User registers with email and password (minimum 8 characters)
    2. OTP (6-digit code) is sent to user's email
    3. User must verify OTP using `/auth/verify-otp` endpoint
    4. After verification, user receives JWT token and can login with password
    
    **Note:** In development mode, OTP is printed to console if SMTP is not configured.
    
    **Friend Invitation:**
    - If you received an invitation link, the `invitation_token` will be automatically included
    - This will automatically add you as friends with the person who invited you
    
    **Next Steps:**
    - Check your email (or console) for the OTP code
    - Use the `user_id` from response to verify OTP at `/auth/verify-otp`
    """
)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # Normalize email (lowercase)
    email = user_data.email.lower().strip()
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    try:
        # Create new user (email not verified yet)
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=email,
            password_hash=hashed_password,
            name=user_data.name,
            email_verified=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Handle friend invitation if token is provided
        if user_data.invitation_token:
            invitation = invitation_service.get_invitation_by_token(
                db=db,
                token=user_data.invitation_token
            )
            
            if invitation:
                # Get inviter
                inviter = invitation_service.get_inviter(db=db, inviter_id=invitation.inviter_id)
                
                if inviter:
                    # Create bidirectional friendship
                    friendship1 = Friend(
                        user_id=new_user.id,
                        friend_id=inviter.id
                    )
                    friendship2 = Friend(
                        user_id=inviter.id,
                        friend_id=new_user.id
                    )
                    
                    db.add(friendship1)
                    db.add(friendship2)
                    
                    # Mark invitation as accepted
                    invitation_service.accept_invitation(db=db, invitation=invitation)
        
        # Generate and send OTP
        otp = otp_service.generate_otp(new_user.id, email)
        email_service.send_otp_email(email, otp, user_data.name)
        
        return RegisterResponse(
            message="Registration successful! Please check your email for OTP verification code.",
            user_id=new_user.id,
            email=new_user.email,
            email_verified=False
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during registration: {str(e)}"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user",
    description="""
    Login user and return JWT access token.
    
    **Requirements:**
    - User must have verified their email using OTP before login
    - If email is not verified, use `/auth/resend-otp` to get a new OTP
    
    **Response:**
    - Returns JWT access token
    - Use token in Authorization header: `Bearer <token>`
    - Token is required for protected endpoints like `/auth/me`
    """
)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # Normalize email
    email = user_data.email.lower().strip()
    
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if email is verified
    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in. Check your email for OTP or use /auth/resend-otp"
        )
    
    # Verify password
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            email_verified=user.email_verified
        )
    )


@router.post(
    "/verify-otp",
    response_model=TokenResponse,
    summary="Verify OTP and activate account",
    description="""
    Verify OTP code and activate user account.
    
    **What happens:**
    - User's email is marked as verified
    - User receives JWT access token
    - User can now login with password at `/auth/login`
    
    **How to use:**
    1. Get `user_id` from registration response
    2. Get OTP from email (or console in dev mode)
    3. Submit both to this endpoint
    4. Receive JWT token for authentication
    
    **OTP Details:**
    - OTP is 6 digits
    - Valid for 10 minutes
    - Maximum 5 verification attempts
    """
)
def verify_otp(otp_data: OTPVerify, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.id == otp_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Verify OTP
    if not otp_service.verify_otp(otp_data.user_id, user.email, otp_data.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    try:
        # Mark email as verified
        user.email_verified = True
        db.commit()
        db.refresh(user)
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                email_verified=True
            )
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during verification: {str(e)}"
        )


@router.post(
    "/resend-otp",
    status_code=status.HTTP_200_OK,
    summary="Resend OTP code",
    description="""
    Resend OTP verification code to user's email.
    
    **When to use:**
    - User didn't receive the email
    - OTP expired (valid for 10 minutes)
    - User wants a new OTP code
    - Previous OTP was lost
    
    **Note:** Only works for unverified accounts. If email is already verified, this endpoint will return an error.
    """
)
def resend_otp(otp_data: OTPResend, db: Session = Depends(get_db)):
    # Normalize email
    email = otp_data.email.lower().strip()
    
    # Find user
    user = db.query(User).filter(User.id == otp_data.user_id, User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already verified
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate and send new OTP
    otp = otp_service.generate_otp(user.id, email)
    email_service.send_otp_email(email, otp, user.name)
    
    return {
        "message": "OTP has been resent to your email",
        "user_id": user.id,
        "email": email
    }


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user information",
    description="""
    Get information about the currently authenticated user.
    
    **Authentication Required:**
    - Requires valid JWT token in Authorization header
    - Format: `Authorization: Bearer <token>`
    
    **Response includes:**
    - User ID
    - Email address
    - Name (if provided)
    - Email verification status
    """
)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        email_verified=current_user.email_verified
    )

