import secrets
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.invitation import FriendInvitation
from app.models.user import User


class InvitationService:
    """Service for managing friend invitations"""
    
    def __init__(self):
        self.invitation_expiry_days = 7  # Invitations expire in 7 days
    
    def create_invitation(
        self, 
        db: Session,
        inviter_id: UUID, 
        invitee_email: str
    ) -> FriendInvitation:
        """
        Create a new friend invitation
        
        Args:
            db: Database session
            inviter_id: User ID of the person sending the invitation
            invitee_email: Email address of the person being invited
            
        Returns:
            FriendInvitation: The created invitation
        """
        # Generate secure invitation token
        invitation_token = secrets.token_urlsafe(32)
        
        # Calculate expiration date
        expires_at = datetime.utcnow() + timedelta(days=self.invitation_expiry_days)
        
        # Check if there's an existing pending invitation
        existing_invitation = db.query(FriendInvitation).filter(
            FriendInvitation.inviter_id == inviter_id,
            FriendInvitation.invitee_email == invitee_email.lower(),
            FriendInvitation.accepted == False,
            FriendInvitation.expires_at > datetime.utcnow()
        ).first()
        
        if existing_invitation:
            # Reuse existing invitation, update expiry
            existing_invitation.expires_at = expires_at
            existing_invitation.invitation_token = invitation_token
            db.commit()
            db.refresh(existing_invitation)
            return existing_invitation
        
        # Create new invitation
        invitation = FriendInvitation(
            inviter_id=inviter_id,
            invitee_email=invitee_email.lower(),
            invitation_token=invitation_token,
            expires_at=expires_at,
            accepted=False
        )
        
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        
        return invitation
    
    def get_invitation_by_token(
        self, 
        db: Session, 
        token: str
    ) -> Optional[FriendInvitation]:
        """
        Get invitation by token
        
        Args:
            db: Database session
            token: Invitation token
            
        Returns:
            Optional[FriendInvitation]: The invitation if found and valid, None otherwise
        """
        invitation = db.query(FriendInvitation).filter(
            FriendInvitation.invitation_token == token,
            FriendInvitation.accepted == False,
            FriendInvitation.expires_at > datetime.utcnow()
        ).first()
        
        return invitation
    
    def accept_invitation(
        self, 
        db: Session, 
        invitation: FriendInvitation
    ) -> bool:
        """
        Mark invitation as accepted
        
        Args:
            db: Database session
            invitation: The invitation to accept
            
        Returns:
            bool: True if successful
        """
        invitation.accepted = True
        db.commit()
        return True
    
    def get_inviter(
        self, 
        db: Session, 
        inviter_id: UUID
    ) -> Optional[User]:
        """
        Get the user who sent the invitation
        
        Args:
            db: Database session
            inviter_id: User ID of the inviter
            
        Returns:
            Optional[User]: The inviter user if found
        """
        return db.query(User).filter(User.id == inviter_id).first()


# Global instance
invitation_service = InvitationService()

