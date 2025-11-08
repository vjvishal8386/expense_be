from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base
import uuid


class FriendInvitation(Base):
    __tablename__ = "friend_invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    inviter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    invitee_email = Column(String, nullable=False, index=True)
    invitation_token = Column(String, unique=True, nullable=False, index=True)
    accepted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def __repr__(self):
        return f"<FriendInvitation(inviter_id={self.inviter_id}, invitee_email={self.invitee_email})>"

