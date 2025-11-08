from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class FriendAdd(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Friend's email address",
        example="friend@example.com"
    )
    name: Optional[str] = Field(
        None,
        description="Friend's name (optional)",
        example="John Doe"
    )


class FriendResponse(BaseModel):
    id: UUID = Field(..., description="Friend's user ID", example="123e4567-e89b-12d3-a456-426614174000")
    email: str = Field(..., description="Friend's email", example="friend@example.com")
    name: Optional[str] = Field(None, description="Friend's name", example="John Doe")
    email_verified: bool = Field(False, description="Whether friend has verified their email", example=True)

    class Config:
        from_attributes = True


class FriendInviteRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Email address to invite",
        example="newuser@example.com"
    )
    name: Optional[str] = Field(
        None,
        description="Optional name of the person to invite",
        example="Jane Smith"
    )


class FriendInviteResponse(BaseModel):
    message: str
    invitation_sent: bool
    friend_exists: bool
    friend: Optional[FriendResponse] = None

