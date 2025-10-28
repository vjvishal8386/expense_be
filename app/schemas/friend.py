from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class FriendAdd(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class FriendResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str] = None

    class Config:
        from_attributes = True

