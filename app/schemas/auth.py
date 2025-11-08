from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class UserRegister(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        description="User's password (minimum 8 characters)",
        example="securepassword123",
        min_length=8
    )
    name: Optional[str] = Field(
        None,
        description="User's full name (optional)",
        example="John Doe"
    )
    invitation_token: Optional[str] = Field(
        None,
        description="Friend invitation token (optional - received via email invite)",
        example="abc123xyz789"
    )


class UserLogin(BaseModel):
    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )
    password: str = Field(
        ...,
        description="User's password",
        example="securepassword123"
    )


class UserResponse(BaseModel):
    id: UUID = Field(..., description="Unique user identifier", example="123e4567-e89b-12d3-a456-426614174000")
    email: str = Field(..., description="User's email address", example="user@example.com")
    name: Optional[str] = Field(None, description="User's full name", example="John Doe")
    email_verified: bool = Field(False, description="Email verification status", example=True)

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "John Doe",
                "email_verified": True
            }
        }


class TokenResponse(BaseModel):
    access_token: str = Field(
        ...,
        description="JWT access token (use this in Authorization header: Bearer <token>)",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    token_type: str = Field(
        "bearer",
        description="Token type",
        example="bearer"
    )
    user: UserResponse = Field(..., description="User information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjNlNDU2Ny1lODliLTEyZDMtYTQ1Ni00MjY2MTQxNzQwMDAiLCJleHAiOjE2OTk5OTk5OTl9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "name": "John Doe",
                    "email_verified": True
                }
            }
        }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[UUID] = None


class OTPVerify(BaseModel):
    user_id: UUID = Field(
        ...,
        description="User ID received from registration endpoint",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    otp: str = Field(
        ...,
        description="6-digit OTP code sent to user's email",
        example="123456",
        min_length=6,
        max_length=6
    )


class OTPResend(BaseModel):
    user_id: UUID = Field(
        ...,
        description="User ID received from registration endpoint",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )


class RegisterResponse(BaseModel):
    message: str = Field(
        ...,
        description="Success message",
        example="Registration successful! Please check your email for OTP verification code."
    )
    user_id: UUID = Field(
        ...,
        description="Unique user identifier (use this for OTP verification)",
        example="123e4567-e89b-12d3-a456-426614174000"
    )
    email: str = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )
    email_verified: bool = Field(
        False,
        description="Email verification status (will be false until OTP is verified)",
        example=False
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Registration successful! Please check your email for OTP verification code.",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "email_verified": False
            }
        }

