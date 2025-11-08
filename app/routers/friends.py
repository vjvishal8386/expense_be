from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.friend import Friend
from app.schemas.friend import FriendAdd, FriendResponse, FriendInviteRequest, FriendInviteResponse
from app.dependencies import get_current_user
from app.services.sendgrid_email_service import email_service
from app.services.invitation_service import invitation_service

router = APIRouter(prefix="/friends", tags=["Friends"])


@router.get("", response_model=List[FriendResponse])
def get_friends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all friends of the current user
    """
    # Query friends table where current user is the user_id
    friend_relationships = db.query(Friend).filter(
        Friend.user_id == current_user.id
    ).all()
    
    # Extract friend IDs
    friend_ids = [rel.friend_id for rel in friend_relationships]
    
    # Get user details for all friends
    friends = db.query(User).filter(User.id.in_(friend_ids)).all()
    
    return [
        FriendResponse(
            id=friend.id,
            email=friend.email,
            name=friend.name,
            email_verified=friend.email_verified
        )
        for friend in friends
    ]


@router.post(
    "/invite",
    response_model=FriendInviteResponse,
    status_code=status.HTTP_200_OK,
    summary="Invite friend by email",
    description="""
    Invite a friend via email to join and automatically connect.
    
    **Two scenarios:**
    1. **Friend already has account**: Sends friend request notification email
    2. **Friend doesn't have account**: Sends invitation email with registration link
    
    The invitation link contains a token that automatically creates friendship upon registration.
    """
)
def invite_friend(
    invite_data: FriendInviteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite a friend by email
    """
    # Normalize email
    email = invite_data.email.lower().strip()
    
    # Check if trying to invite self
    if email == current_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot invite yourself"
        )
    
    # Check if friend already exists
    friend_user = db.query(User).filter(User.email == email).first()
    
    if friend_user:
        # Friend already has an account
        # Check if already friends
        existing_friendship = db.query(Friend).filter(
            Friend.user_id == current_user.id,
            Friend.friend_id == friend_user.id
        ).first()
        
        if existing_friendship:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already friends with this user"
            )
        
        # Create bidirectional friendship
        friendship1 = Friend(
            user_id=current_user.id,
            friend_id=friend_user.id
        )
        friendship2 = Friend(
            user_id=friend_user.id,
            friend_id=current_user.id
        )
        
        db.add(friendship1)
        db.add(friendship2)
        db.commit()
        
        # Send notification email to friend
        email_service.send_friend_request_notification(
            to_email=friend_user.email,
            requester_name=current_user.name or current_user.email,
            to_name=friend_user.name
        )
        
        return FriendInviteResponse(
            message=f"Friend request sent to {friend_user.email}",
            invitation_sent=True,
            friend_exists=True,
            friend=FriendResponse(
                id=friend_user.id,
                email=friend_user.email,
                name=friend_user.name,
                email_verified=friend_user.email_verified
            )
        )
    
    else:
        # Friend doesn't have an account yet
        # Create invitation
        invitation = invitation_service.create_invitation(
            db=db,
            inviter_id=current_user.id,
            invitee_email=email
        )
        
        # Send invitation email
        email_service.send_friend_invitation_email(
            to_email=email,
            inviter_name=current_user.name or current_user.email,
            invitation_token=invitation.invitation_token
        )
        
        return FriendInviteResponse(
            message=f"Invitation sent to {email}. They will be added as your friend when they sign up.",
            invitation_sent=True,
            friend_exists=False,
            friend=None
        )


@router.post("", response_model=FriendResponse, status_code=status.HTTP_201_CREATED)
def add_friend(
    friend_data: FriendAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a friend by email (legacy endpoint - use /friends/invite instead)
    
    Creates bidirectional friendship. If friend doesn't exist, creates a pending user account.
    """
    # Normalize email
    email = friend_data.email.lower().strip()
    
    # Check if trying to add self
    if email == current_user.email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add yourself as a friend"
        )
    
    # Check if friend exists in users table
    friend_user = db.query(User).filter(User.email == email).first()
    
    # If friend doesn't exist, create a new user (pending friend)
    if not friend_user:
        # Create a temporary password hash for the new user
        # They can later register with their own password
        from app.security import get_password_hash
        import secrets
        
        temp_password = secrets.token_urlsafe(32)
        friend_user = User(
            email=email,
            password_hash=get_password_hash(temp_password),
            name=friend_data.name,
            email_verified=False
        )
        db.add(friend_user)
        db.commit()
        db.refresh(friend_user)
    
    # Check if friendship already exists
    existing_friendship = db.query(Friend).filter(
        Friend.user_id == current_user.id,
        Friend.friend_id == friend_user.id
    ).first()
    
    if existing_friendship:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friend already added"
        )
    
    # Create bidirectional friendship
    # Direction 1: current_user -> friend_user
    friendship1 = Friend(
        user_id=current_user.id,
        friend_id=friend_user.id
    )
    # Direction 2: friend_user -> current_user
    friendship2 = Friend(
        user_id=friend_user.id,
        friend_id=current_user.id
    )
    
    db.add(friendship1)
    db.add(friendship2)
    db.commit()
    
    return FriendResponse(
        id=friend_user.id,
        email=friend_user.email,
        name=friend_user.name,
        email_verified=friend_user.email_verified
    )

