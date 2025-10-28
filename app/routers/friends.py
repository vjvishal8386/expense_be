from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.friend import Friend
from app.schemas.friend import FriendAdd, FriendResponse
from app.dependencies import get_current_user

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
            name=friend.name
        )
        for friend in friends
    ]


@router.post("", response_model=FriendResponse, status_code=status.HTTP_201_CREATED)
def add_friend(
    friend_data: FriendAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a friend by email. Creates bidirectional friendship.
    If friend doesn't exist, creates a new user account.
    """
    # Check if trying to add self
    if friend_data.email == current_user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add yourself as a friend"
        )
    
    # Check if friend exists in users table
    friend_user = db.query(User).filter(User.email == friend_data.email).first()
    
    # If friend doesn't exist, create a new user (pending friend)
    if not friend_user:
        # Create a temporary password hash for the new user
        # They can later register with their own password
        from app.security import get_password_hash
        import secrets
        
        temp_password = secrets.token_urlsafe(32)
        friend_user = User(
            email=friend_data.email,
            password_hash=get_password_hash(temp_password),
            name=friend_data.name
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
        name=friend_user.name
    )

